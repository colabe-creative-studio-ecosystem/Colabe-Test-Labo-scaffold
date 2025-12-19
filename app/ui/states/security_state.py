import reflex as rx
from app.ui.states.auth_state import AuthState
from app.core.models import (
    SecurityFinding,
    SBOMComponent,
    ComponentVulnerability,
    Project,
)
import sqlmodel
from sqlalchemy.orm import selectinload
import subprocess
import json
import os
import tempfile
import requests
import asyncio
import logging


class VulnerabilityDisplay(rx.Base):
    id: int | None = None
    severity: str
    summary: str


class SBOMComponentDisplay(rx.Base):
    name: str
    version: str
    vulnerabilities: list[VulnerabilityDisplay]


class SecurityState(rx.State):
    security_findings: list[SecurityFinding] = []
    sbom_components: list[SBOMComponentDisplay] = []
    current_project_id: int | None = 1

    @rx.event
    async def load_security_data(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_logged_in or not self.current_project_id:
            return
        with rx.session() as session:
            self.security_findings = session.exec(
                sqlmodel.select(SecurityFinding).where(
                    SecurityFinding.project_id == self.current_project_id
                )
            ).all()
            components = session.exec(
                sqlmodel.select(SBOMComponent)
                .where(SBOMComponent.project_id == self.current_project_id)
                .options(selectinload(SBOMComponent.vulnerabilities))
            ).all()
            self.sbom_components = [
                SBOMComponentDisplay(
                    name=c.name,
                    version=c.version,
                    vulnerabilities=[
                        VulnerabilityDisplay(
                            id=v.id, severity=v.severity, summary=v.summary
                        )
                        for v in c.vulnerabilities
                    ],
                )
                for c in components
            ]

    @rx.event(background=True)
    async def run_security_scans(self):
        repo_path = os.path.abspath(".")
        async with self:
            if not self.current_project_id:
                return
            with rx.session() as session:
                session.exec(
                    sqlmodel.delete(SecurityFinding).where(
                        SecurityFinding.project_id == self.current_project_id
                    )
                )
                session.commit()
        await asyncio.to_thread(
            self._run_bandit_scan, repo_path, self.current_project_id
        )
        await asyncio.to_thread(
            self._run_cyclonedx_scan, repo_path, self.current_project_id
        )
        async with self:
            await self.load_security_data()

    def _run_bandit_scan(self, repo_path: str, project_id: int):
        try:
            result = subprocess.run(
                ["bandit", "-r", repo_path, "-f", "json"],
                capture_output=True,
                text=True,
            )
        except Exception as e:
            logging.exception(f"Bandit scan error: {e}")
            return
        if result.returncode > 0 and result.stdout:
            try:
                report = json.loads(result.stdout)
                with rx.session() as session:
                    for finding_data in report.get("results", []):
                        cwe_id = finding_data.get("cwe", {}).get("id")
                        cwe_val = str(cwe_id) if cwe_id is not None else None
                        finding = SecurityFinding(
                            project_id=project_id,
                            scanner="bandit",
                            test_id=finding_data["test_id"],
                            description=finding_data["issue_text"],
                            severity=finding_data["issue_severity"],
                            file_path=finding_data["filename"].replace(repo_path, ""),
                            line_number=finding_data["line_number"],
                            cwe=cwe_val,
                            owasp_category=self._map_cwe_to_owasp(
                                finding_data.get("cwe", {}).get("id")
                            ),
                        )
                        session.add(finding)
                    session.commit()
            except json.JSONDecodeError:
                logging.exception("Error decoding bandit JSON output")

    def _run_cyclonedx_scan(self, repo_path: str, project_id: int):
        req_file = os.path.join(repo_path, "requirements.txt")
        if not os.path.exists(req_file):
            return
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as outf:
            output_file = outf.name
        try:
            subprocess.run(
                ["cyclonedx-py", "requirements", req_file, "-o", output_file],
                capture_output=True,
                text=True,
            )
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    sbom = json.load(f)
                with rx.session() as session:
                    session.exec(
                        sqlmodel.delete(SBOMComponent).where(
                            SBOMComponent.project_id == project_id
                        )
                    )
                    session.commit()
                    components = sbom.get("components", [])
                    for comp_data in components:
                        comp = SBOMComponent(
                            project_id=project_id,
                            name=comp_data["name"],
                            version=comp_data["version"],
                            purl=comp_data["purl"],
                        )
                        session.add(comp)
                    session.commit()
                    self._check_osv(project_id)
        except Exception as e:
            logging.exception(f"CycloneDX scan error: {e}")
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def _check_osv(self, project_id: int):
        with rx.session() as session:
            components = session.exec(
                sqlmodel.select(SBOMComponent).where(
                    SBOMComponent.project_id == project_id
                )
            ).all()
            queries = []
            for comp in components:
                queries.append(
                    {
                        "package": {"name": comp.name, "ecosystem": "PyPI"},
                        "version": comp.version,
                    }
                )
            if not queries:
                return
            response = requests.post(
                "https://api.osv.dev/v1/querybatch", json={"queries": queries}
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                for i, res in enumerate(results):
                    if "vulns" in res:
                        comp = components[i]
                        for vuln_data in res["vulns"]:
                            severity = "UNKNOWN"
                            cvss_score = None
                            if vuln_data.get("severity"):
                                for sev in vuln_data["severity"]:
                                    if sev.get("type") == "CVSS_V3":
                                        severity = sev.get("database_specific", {}).get(
                                            "severity", "UNKNOWN"
                                        )
                                        cvss_score = (
                                            float(sev.get("score"))
                                            if sev.get("score")
                                            else None
                                        )
                                        break
                            vuln = ComponentVulnerability(
                                component_id=comp.id,
                                osv_id=vuln_data["id"],
                                summary=vuln_data.get(
                                    "summary", "No summary available."
                                ),
                                severity=severity,
                                cvss_score=cvss_score,
                                details=json.dumps(vuln_data),
                            )
                            if not session.exec(
                                sqlmodel.select(ComponentVulnerability).where(
                                    ComponentVulnerability.osv_id == vuln.osv_id
                                )
                            ).first():
                                session.add(vuln)
                session.commit()

    def _map_cwe_to_owasp(self, cwe_id: int | None) -> str | None:
        if cwe_id is None:
            return None
        owasp_mapping = {
            "A01:2021-Broken Access Control": [
                22,
                23,
                35,
                59,
                200,
                201,
                219,
                264,
                275,
                276,
                284,
                285,
                352,
                359,
                377,
                402,
                425,
                441,
                497,
                538,
                540,
                548,
                552,
                566,
                601,
                639,
                651,
                668,
                706,
                862,
                863,
                913,
                922,
                1275,
            ],
            "A02:2021-Cryptographic Failures": [
                259,
                261,
                296,
                310,
                311,
                312,
                313,
                316,
                319,
                321,
                322,
                323,
                324,
                325,
                326,
                327,
                328,
                329,
                330,
                331,
                335,
                336,
                337,
                338,
                340,
                347,
                523,
                720,
                757,
                759,
                760,
                780,
            ],
            "A03:2021-Injection": [
                20,
                74,
                75,
                77,
                78,
                79,
                80,
                83,
                87,
                88,
                89,
                90,
                91,
                93,
                94,
                95,
                96,
                97,
                98,
                99,
                100,
                113,
                116,
                138,
                184,
                470,
                471,
                564,
                610,
                643,
                644,
                652,
                917,
            ],
            "A04:2021-Insecure Design": [
                73,
                183,
                209,
                213,
                235,
                250,
                256,
                257,
                266,
                269,
                280,
                311,
                312,
                313,
                316,
                419,
                430,
                434,
                444,
                451,
                472,
                501,
                522,
                525,
                539,
                579,
                598,
                602,
                642,
                646,
                650,
                653,
                656,
                657,
                799,
                807,
                840,
                841,
                927,
                1021,
                1173,
            ],
            "A05:2021-Security Misconfiguration": [
                2,
                11,
                13,
                15,
                16,
                260,
                315,
                520,
                526,
                537,
                541,
                547,
                611,
                614,
                756,
                776,
                942,
                1004,
                1032,
                1174,
            ],
            "A06:2021-Vulnerable and Outdated Components": [937, 1035, 1104],
            "A07:2021-Identification and Authentication Failures": [
                255,
                259,
                287,
                288,
                290,
                294,
                295,
                297,
                300,
                302,
                303,
                304,
                306,
                307,
                346,
                384,
                521,
                613,
                620,
                640,
                798,
                804,
                836,
                916,
            ],
            "A08:2021-Software and Data Integrity Failures": [
                345,
                353,
                426,
                494,
                502,
                565,
                784,
                829,
                830,
                915,
            ],
            "A09:2021-Security Logging and Monitoring Failures": [117, 223, 532, 778],
            "A10:2021-Server-Side Request Forgery": [918],
        }
        for owasp_cat, cwe_list in owasp_mapping.items():
            if cwe_id in cwe_list:
                return owasp_cat.split("-")[0]
        return None