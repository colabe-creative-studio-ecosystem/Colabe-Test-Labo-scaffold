import reflex as rx
from app.ui.states.auth_state import AuthState


def auth_layout(child: rx.Component) -> rx.Component:
    return rx.el.div(
        child,
        class_name="min-h-screen flex items-center justify-center colabe-bg font-['Inter']",
    )


def auth_card(
    title: str,
    subtitle: str,
    form: rx.Component,
    link_text: str,
    link_href: str,
    link_prompt: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("flask-conical", size=32, class_name="text-accent-cyan"),
            class_name="mx-auto mb-6 w-fit p-3 rounded-full bg-accent-cyan/10",
        ),
        rx.el.h1(title, class_name="text-2xl font-bold text-center text-text-primary"),
        rx.el.p(subtitle, class_name="text-sm text-text-secondary text-center mt-1"),
        form,
        rx.el.p(
            link_prompt,
            " ",
            rx.el.a(
                link_text,
                href=link_href,
                class_name="text-accent-cyan hover:underline font-medium",
            ),
            class_name="text-center text-sm text-text-secondary mt-6",
        ),
        rx.el.p(
            AuthState.error_message, class_name="text-danger text-sm mt-4 text-center"
        ),
        class_name="w-full max-w-md p-8 space-y-6 bg-bg-elevated rounded-xl shadow-lg border border-white/10",
    )


def login_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.label("Email", class_name="text-sm font-medium text-text-secondary"),
            rx.el.input(
                placeholder="user@example.com",
                type="email",
                id="email",
                name="email",
                class_name="w-full px-4 py-2 mt-1 bg-bg-base border border-white/20 rounded-lg focus:ring-accent-cyan focus:border-accent-cyan",
            ),
            class_name="space-y-1",
        ),
        rx.el.div(
            rx.el.label(
                "Password", class_name="text-sm font-medium text-text-secondary"
            ),
            rx.el.input(
                placeholder="••••••••",
                type="password",
                id="password",
                name="password",
                class_name="w-full px-4 py-2 mt-1 bg-bg-base border border-white/20 rounded-lg focus:ring-accent-cyan focus:border-accent-cyan",
            ),
            class_name="space-y-1",
        ),
        rx.el.button(
            "Sign In",
            type="submit",
            class_name="w-full py-2 px-4 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-accent-cyan focus:ring-opacity-50",
        ),
        on_submit=AuthState.login,
        class_name="mt-6 space-y-4",
    )


def register_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.label(
                "Tenant Name", class_name="text-sm font-medium text-text-secondary"
            ),
            rx.el.input(
                placeholder="Your Company Inc.",
                id="tenant_name",
                name="tenant_name",
                class_name="w-full px-4 py-2 mt-1 bg-bg-base border border-white/20 rounded-lg focus:ring-accent-cyan focus:border-accent-cyan",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Username", class_name="text-sm font-medium text-text-secondary"
            ),
            rx.el.input(
                placeholder="john_doe",
                id="username",
                name="username",
                class_name="w-full px-4 py-2 mt-1 bg-bg-base border border-white/20 rounded-lg focus:ring-accent-cyan focus:border-accent-cyan",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Email address", class_name="text-sm font-medium text-text-secondary"
            ),
            rx.el.input(
                placeholder="user@example.com",
                type="email",
                id="email",
                name="email",
                class_name="w-full px-4 py-2 mt-1 bg-bg-base border border-white/20 rounded-lg focus:ring-accent-cyan focus:border-accent-cyan",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Password", class_name="text-sm font-medium text-text-secondary"
            ),
            rx.el.input(
                placeholder="••••••••",
                type="password",
                id="password",
                name="password",
                class_name="w-full px-4 py-2 mt-1 bg-bg-base border border-white/20 rounded-lg focus:ring-accent-cyan focus:border-accent-cyan",
            ),
        ),
        rx.el.button(
            "Create Account",
            type="submit",
            class_name="w-full py-2 px-4 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-accent-cyan focus:ring-opacity-50",
        ),
        on_submit=AuthState.register,
        class_name="mt-6 space-y-4",
    )


def login_page() -> rx.Component:
    return auth_layout(
        auth_card(
            title="Sign in to your account",
            subtitle="Welcome back to Colabe Test Labo",
            form=login_form(),
            link_text="Sign up",
            link_href="/register",
            link_prompt="Don't have an account?",
        )
    )


def register_page() -> rx.Component:
    return auth_layout(
        auth_card(
            title="Create a new account",
            subtitle="Join Colabe Test Labo",
            form=register_form(),
            link_text="Sign In",
            link_href="/login",
            link_prompt="Already have an account?",
        )
    )