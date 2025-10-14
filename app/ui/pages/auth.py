import reflex as rx
from app.ui.states.auth_state import AuthState


def auth_layout(child: rx.Component) -> rx.Component:
    return rx.el.div(
        child,
        class_name="min-h-screen flex items-center justify-center bg-gray-50 font-['Inter']",
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
            rx.icon("flask-conical", size=32, class_name="text-blue-500"),
            class_name="mx-auto mb-6 w-fit p-3 rounded-full bg-blue-100",
        ),
        rx.el.h1(title, class_name="text-2xl font-bold text-center text-gray-900"),
        rx.el.p(subtitle, class_name="text-sm text-gray-500 text-center mt-1"),
        form,
        rx.el.p(
            link_prompt,
            " ",
            rx.el.a(
                link_text,
                href=link_href,
                class_name="text-blue-500 hover:underline font-medium",
            ),
            class_name="text-center text-sm text-gray-600 mt-6",
        ),
        rx.el.p(
            AuthState.error_message, class_name="text-red-500 text-sm mt-4 text-center"
        ),
        class_name="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg border border-gray-200",
    )


def login_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.label("Email", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="user@example.com",
                type="email",
                id="email",
                class_name="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
            ),
            class_name="space-y-1",
        ),
        rx.el.div(
            rx.el.label("Password", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="••••••••",
                type="password",
                id="password",
                class_name="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
            ),
            class_name="space-y-1",
        ),
        rx.el.button(
            "Sign In",
            type="submit",
            class_name="w-full py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50",
        ),
        on_submit=AuthState.login,
        class_name="mt-6 space-y-4",
    )


def register_form() -> rx.Component:
    return rx.el.form(
        rx.el.div(
            rx.el.label("Tenant Name", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="Your Company Inc.",
                id="tenant_name",
                class_name="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
            ),
        ),
        rx.el.div(
            rx.el.label("Username", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="john_doe",
                id="username",
                class_name="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "Email address", class_name="text-sm font-medium text-gray-700"
            ),
            rx.el.input(
                placeholder="user@example.com",
                type="email",
                id="email",
                class_name="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
            ),
        ),
        rx.el.div(
            rx.el.label("Password", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="••••••••",
                type="password",
                id="password",
                class_name="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500",
            ),
        ),
        rx.el.button(
            "Create Account",
            type="submit",
            class_name="w-full py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50",
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