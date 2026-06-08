"""Premium-feeling local desktop UI for the prompt assistant beta."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from project_360_degree_ai_prompt_assistant_platform.assistant import PromptAssistant
from project_360_degree_ai_prompt_assistant_platform.guided import (
    GuidedPromptBlueprint,
    suggest_prompt_upgrades,
)
from project_360_degree_ai_prompt_assistant_platform.pack_catalog import PACK_CATALOG


QUESTION_FLOW_BY_MODE = {
    "Quick": [
        ("goal", "What should a strong answer help the reader do?", "One sentence is enough."),
        ("output_type", "What kind of output do you want?", "Example: email, landing page, memo, plan."),
    ],
    "Guided": [
        ("goal", "What should success look like after the answer?", "Skip if the app can infer it."),
        ("recipient", "Who is this for?", "Example: startup founders, students, hiring manager."),
        ("output_type", "What type of output do you want?", "Example: email, landing page, memo, proposal."),
        ("desired_action", "After they read it, what should they do?", "Example: book a demo, approve the plan, reply."),
        ("avoid", "What should it avoid sounding like?", "Example: generic AI buzzwords, too formal, robotic."),
    ],
    "Expert": [
        ("goal", "What should success look like after the answer?", "Be precise about the outcome."),
        ("recipient", "Who is this for?", "Name the exact audience or decision-maker."),
        ("output_type", "What output do you want?", "Example: brief, plan, script, memo, landing page."),
        ("desired_action", "What action or decision should this drive?", "Name the ideal next step."),
        ("avoid", "What should it avoid sounding like?", "Example: vague, robotic, jargon-heavy."),
        ("success_criteria", "How will you judge whether this prompt worked?", "Example: gets replies, drives signups, feels premium."),
        ("tone", "What tone should the final prompt push toward?", "Example: premium, persuasive, concise, technical."),
    ],
}

MODE_DESCRIPTIONS = {
    "Quick": "Fastest path. The app asks only the highest-value questions.",
    "Guided": "Balanced coaching. Great default for most testers.",
    "Expert": "Deeper build. Adds stronger criteria, tone, and more deliberate structure.",
}

FIELD_PROMPTS = {
    "goal": (
        "What should a strong answer help the reader do or understand?",
        "One sentence is enough. Focus on the result, not the topic alone.",
    ),
    "recipient": (
        "Who is this really for?",
        "Example: startup founders, junior developers, students, hiring managers.",
    ),
    "output_type": (
        "What kind of output should the model return?",
        "Example: email, proposal, checklist, table, study guide, scene outline.",
    ),
    "desired_action": (
        "After reading it, what should happen next?",
        "Example: reply, approve, understand, buy, fix, study, sign up.",
    ),
    "avoid": (
        "What should the output avoid sounding like?",
        "Example: vague, robotic, overhyped, too formal, generic AI language.",
    ),
    "success_criteria": (
        "How will you judge whether this prompt worked?",
        "Example: gets replies, feels clear, produces a usable table, avoids fluff.",
    ),
    "tone": (
        "What tone should the final prompt push toward?",
        "Example: premium, concise, friendly, technical, persuasive.",
    ),
    "constraints_text": (
        "Any hard rules or constraints to add?",
        "Example: keep under 120 words, use bullets, avoid jargon, only use provided facts.",
    ),
}

REPAIR_FIELD_ALIASES = {
    "audience": "recipient",
    "recipient": "recipient",
    "recipient_role": "recipient",
    "client_type": "recipient",
    "stakeholders": "recipient",
    "goal": "goal",
    "search_intent": "goal",
    "main_takeaway": "goal",
    "main_benefit": "goal",
    "code_goal": "goal",
    "call_goal": "goal",
    "decision_goal": "goal",
    "comparison_goal": "goal",
    "scene_goal": "goal",
    "expected_outcome": "goal",
    "research_gap": "goal",
    "output format": "output_type",
    "format": "output_type",
    "tone": "tone",
    "desired action": "desired_action",
    "cta": "desired_action",
    "follow_up": "desired_action",
    "constraints": "constraints_text",
    "word limit": "constraints_text",
    "time limit": "constraints_text",
    "timeframe": "constraints_text",
    "timeline": "constraints_text",
    "exam_date": "constraints_text",
    "time_available": "constraints_text",
    "success criteria": "success_criteria",
}


@dataclass
class DesktopSession:
    task: str = ""
    goal: str = ""
    recipient: str = ""
    output_type: str = ""
    desired_action: str = ""
    avoid: str = ""
    success_criteria: str = ""
    tone: str = "clear and practical"
    constraints_text: str = ""


class PromptAssistantApp:
    def __init__(self, assistant: PromptAssistant) -> None:
        self.assistant = assistant
        self.session = DesktopSession()
        self.question_index = 0
        self.current_result = None
        self.current_inspection = None
        self.current_recommendation: dict | None = None
        self.current_question_flow = QUESTION_FLOW_BY_MODE["Guided"]
        self.question_flow_active = False
        self._context_files: list[str] = []
        self._reference_text = ""
        self._reference_patterns: list[str] = []
        self._history_rows: list[dict] = []
        self._library_rows = []
        self._library_search_after_id: str | None = None
        self._busy_count = 0
        self.ui_state_path = self.assistant.settings.app_home / "ui_state.json"

        self.root = tk.Tk()
        self.root.title("Prompt Assistant Beta")
        self.root.configure(bg="#f3efe8")
        self.root.minsize(1180, 820)
        self._center_window(1280, 900)
        self._build_styles()
        self._build_layout()
        self._on_mode_changed()
        self.refresh_history_tab()
        self.refresh_library_filters()
        self.refresh_library_results()
        self.root.after(150, self._focus_prompt_input)
        self.root.after(300, self._maybe_show_first_run_picker)

    def run(self) -> None:
        self.root.mainloop()

    def _build_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#f3efe8")
        style.configure("Card.TFrame", background="#fffaf4")
        style.configure("Title.TLabel", background="#f3efe8", foreground="#211a15", font=("Georgia", 23, "bold"))
        style.configure("Body.TLabel", background="#f3efe8", foreground="#43382f", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#fffaf4", foreground="#6b5d50", font=("Segoe UI", 10))
        style.configure("Question.TLabel", background="#fffaf4", foreground="#211a15", font=("Segoe UI Semibold", 12))
        style.configure("Section.TLabel", background="#fffaf4", foreground="#a35c28", font=("Segoe UI Semibold", 10))
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 10))
        style.configure("Secondary.TButton", font=("Segoe UI", 10))
        style.configure("Panel.TNotebook", background="#fffaf4", borderwidth=0)
        style.configure("Panel.TNotebook.Tab", font=("Segoe UI", 10))
        style.configure("Mode.TRadiobutton", background="#fffaf4", foreground="#211a15", font=("Segoe UI", 10))

    def _build_layout(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame")
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        self.main_canvas = tk.Canvas(shell, bg="#f3efe8", highlightthickness=0, bd=0)
        self.main_canvas.grid(row=0, column=0, sticky="nsew")
        main_scroll = ttk.Scrollbar(shell, orient="vertical", command=self.main_canvas.yview)
        main_scroll.grid(row=0, column=1, sticky="ns")
        self.main_canvas.configure(yscrollcommand=main_scroll.set)

        container = ttk.Frame(self.main_canvas, style="App.TFrame", padding=24)
        self.main_canvas_window = self.main_canvas.create_window((0, 0), window=container, anchor="nw")
        container.bind("<Configure>", lambda _event: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind("<Configure>", lambda event: self.main_canvas.itemconfigure(self.main_canvas_window, width=event.width))
        self.main_canvas.bind_all("<MouseWheel>", self._on_main_mousewheel)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=0)
        container.rowconfigure(3, weight=1)

        ttk.Label(container, text="Prompt Assistant Beta", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            container,
            text="Turn a rough thought into a stronger prompt, see why it improved, and keep everything local by default.",
            style="Body.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 18))

        self._build_entry_card(container)
        self._build_side_tabs(container)
        self._build_result_card(container)
        self.side_card.grid_remove()

    def _build_entry_card(self, parent: ttk.Frame) -> None:
        entry_card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        entry_card.grid(row=2, column=0, columnspan=2, sticky="nsew")
        entry_card.columnconfigure(0, weight=1)
        entry_card.rowconfigure(3, weight=1)
        self.entry_card = entry_card

        ttk.Label(entry_card, text="Your rough prompt", style="Question.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            entry_card,
            text="Start simple: type one rough idea, click Analyze Prompt, then only repair what actually needs work.",
            style="Muted.TLabel",
            wraplength=620,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 10))

        self.quick_prompt_var = tk.StringVar()
        self.quick_prompt_entry = ttk.Entry(entry_card, textvariable=self.quick_prompt_var, font=("Segoe UI", 12))
        self.quick_prompt_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.quick_prompt_entry.bind("<Return>", lambda _event: self.start_guided_flow())

        mode_row = ttk.Frame(entry_card, style="Card.TFrame")
        mode_row.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(mode_row, text="Mode", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="Guided")
        for index, mode in enumerate(["Quick", "Guided", "Expert"], start=1):
            ttk.Radiobutton(
                mode_row,
                text=mode,
                value=mode,
                variable=self.mode_var,
                style="Mode.TRadiobutton",
                command=self._on_mode_changed,
            ).grid(row=0, column=index, sticky="w", padx=(12, 0))

        self.mode_hint = ttk.Label(entry_card, text="", style="Muted.TLabel", wraplength=620, justify="left")
        self.mode_hint.grid(row=4, column=0, sticky="w", pady=(0, 8))

        self.long_editor_label = ttk.Label(
            entry_card,
            text="Longer prompt editor (optional)",
            style="Section.TLabel",
        )
        self.long_editor_label.grid(row=5, column=0, sticky="w", pady=(0, 6))

        self.prompt_input = tk.Text(
            entry_card,
            height=7,
            wrap="word",
            font=("Segoe UI", 12),
            bd=0,
            bg="#ffffff",
            fg="#211a15",
            insertbackground="#211a15",
            padx=14,
            pady=14,
        )
        prompt_input_shell = ttk.Frame(entry_card, style="Card.TFrame")
        prompt_input_shell.grid(row=6, column=0, sticky="nsew", pady=(4, 12))
        self.prompt_input_shell = prompt_input_shell
        prompt_input_shell.columnconfigure(0, weight=1)
        prompt_input_shell.rowconfigure(0, weight=1)
        self.prompt_input.grid(in_=prompt_input_shell, row=0, column=0, sticky="nsew")
        prompt_input_scroll = ttk.Scrollbar(prompt_input_shell, orient="vertical", command=self.prompt_input.yview)
        prompt_input_scroll.grid(row=0, column=1, sticky="ns")
        self.prompt_input.configure(yscrollcommand=prompt_input_scroll.set)
        self.prompt_input.insert("1.0", "")

        prompt_actions = ttk.Frame(entry_card, style="Card.TFrame")
        prompt_actions.grid(row=7, column=0, sticky="ew")
        prompt_actions.columnconfigure(4, weight=1)
        self.start_button = ttk.Button(prompt_actions, text="Analyze Prompt", style="Primary.TButton", command=self.start_guided_flow)
        self.start_button.grid(row=0, column=0, sticky="w")
        self.context_button = ttk.Button(prompt_actions, text="Add Context", style="Secondary.TButton", command=self.open_advanced_context)
        self.context_button.grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.refine_button = ttk.Button(prompt_actions, text="Tighten Output", style="Secondary.TButton", command=self.refine_current_output)
        self.refine_button.grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.pack_picker_button = ttk.Button(
            prompt_actions,
            text="Browse Starter Packs",
            style="Secondary.TButton",
            command=self.open_pack_picker,
        )
        self.pack_picker_button.grid(row=0, column=3, sticky="w", padx=(10, 0))
        self.continue_button = ttk.Button(
            prompt_actions,
            text="Open Repair Mode",
            style="Primary.TButton",
            command=self.enter_repair_mode,
            state="disabled",
        )
        self.continue_button.grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.apply_match_button = ttk.Button(
            prompt_actions,
            text="Use Best Match Template",
            style="Secondary.TButton",
            command=self.load_best_match,
            state="disabled",
        )
        self.apply_match_button.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(10, 0))
        self._set_minimal_launch_mode()

    def _build_side_tabs(self, parent: ttk.Frame) -> None:
        side_card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        side_card.grid(row=2, column=1, rowspan=2, sticky="nsew")
        self.side_card = side_card
        side_card.columnconfigure(0, weight=1)
        side_card.rowconfigure(0, weight=1)

        self.tabs = ttk.Notebook(side_card, style="Panel.TNotebook")
        self.tabs.grid(row=0, column=0, sticky="nsew")

        self._build_coach_tab(self.tabs)
        self._build_history_tab(self.tabs)
        self._build_library_tab(self.tabs)

    def _build_coach_tab(self, tabs: ttk.Notebook) -> None:
        coach_card = ttk.Frame(tabs, style="Card.TFrame", padding=18)
        coach_card.columnconfigure(0, weight=1)
        coach_card.columnconfigure(1, weight=1)
        coach_card.rowconfigure(6, weight=1)
        tabs.add(coach_card, text="Coach")

        ttk.Label(coach_card, text="Smart coaching", style="Question.TLabel").grid(row=0, column=0, sticky="w")
        self.coach_mode_badge = ttk.Label(coach_card, text="Guided mode", style="Section.TLabel")
        self.coach_mode_badge.grid(row=0, column=1, sticky="e")

        self.suggestion_label = ttk.Label(
            coach_card,
            text="The assistant will suggest stronger prompt ideas here.",
            style="Muted.TLabel",
            wraplength=320,
            justify="left",
        )
        self.suggestion_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 16))

        self.match_label = ttk.Label(
            coach_card,
            text="Best pack matches will appear here after the app checks your prompt health.",
            style="Muted.TLabel",
            wraplength=320,
            justify="left",
        )
        self.match_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        self.question_title = ttk.Label(
            coach_card,
            text="Type a rough prompt, then click Analyze Prompt.",
            style="Question.TLabel",
            wraplength=320,
            justify="left",
        )
        self.question_title.grid(row=3, column=0, columnspan=2, sticky="w")

        self.question_hint = ttk.Label(
            coach_card,
            text="",
            style="Muted.TLabel",
            wraplength=320,
            justify="left",
        )
        self.question_hint.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 10))

        self.answer_entry = ttk.Entry(coach_card, font=("Segoe UI", 11), state="disabled")
        self.answer_entry.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.answer_entry.bind("<Return>", lambda _event: self.next_question())

        controls = ttk.Frame(coach_card, style="Card.TFrame")
        controls.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.skip_button = ttk.Button(controls, text="Skip", style="Secondary.TButton", command=self.skip_question, state="disabled")
        self.skip_button.grid(row=0, column=0, sticky="w")
        self.next_button = ttk.Button(controls, text="Next", style="Primary.TButton", command=self.next_question, state="disabled")
        self.next_button.grid(row=0, column=1, sticky="w", padx=(8, 0))

    def _build_history_tab(self, tabs: ttk.Notebook) -> None:
        history_card = ttk.Frame(tabs, style="Card.TFrame", padding=18)
        history_card.columnconfigure(0, weight=1)
        history_card.rowconfigure(1, weight=1)
        history_card.rowconfigure(3, weight=1)
        tabs.add(history_card, text="History")

        ttk.Label(history_card, text="Prompt history", style="Question.TLabel").grid(row=0, column=0, sticky="w")
        self.history_list = tk.Listbox(
            history_card,
            height=8,
            font=("Segoe UI", 10),
            bd=0,
            bg="#ffffff",
            fg="#211a15",
            activestyle="none",
        )
        self.history_list.grid(row=1, column=0, sticky="nsew", pady=(10, 12))
        self.history_list.bind("<<ListboxSelect>>", lambda _event: self._show_selected_history())

        ttk.Label(history_card, text="Saved prompt preview", style="Section.TLabel").grid(row=2, column=0, sticky="w")
        self.history_preview = tk.Text(
            history_card,
            height=10,
            wrap="word",
            font=("Segoe UI", 10),
            bd=0,
            bg="#ffffff",
            fg="#211a15",
            padx=10,
            pady=10,
        )
        history_preview_shell = ttk.Frame(history_card, style="Card.TFrame")
        history_preview_shell.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
        history_preview_shell.columnconfigure(0, weight=1)
        history_preview_shell.rowconfigure(0, weight=1)
        self.history_preview.grid(in_=history_preview_shell, row=0, column=0, sticky="nsew")
        history_preview_scroll = ttk.Scrollbar(history_preview_shell, orient="vertical", command=self.history_preview.yview)
        history_preview_scroll.grid(row=0, column=1, sticky="ns")
        self.history_preview.configure(yscrollcommand=history_preview_scroll.set)

        history_actions = ttk.Frame(history_card, style="Card.TFrame")
        history_actions.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(history_actions, text="Reload", style="Secondary.TButton", command=self.refresh_history_tab).grid(row=0, column=0, sticky="w")
        ttk.Button(history_actions, text="Load Into Prompt", style="Primary.TButton", command=self.load_selected_history).grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )

    def _build_library_tab(self, tabs: ttk.Notebook) -> None:
        library_card = ttk.Frame(tabs, style="Card.TFrame", padding=18)
        library_card.columnconfigure(0, weight=1)
        library_card.rowconfigure(2, weight=1)
        library_card.rowconfigure(4, weight=1)
        tabs.add(library_card, text="Packs")

        ttk.Label(library_card, text="Prompt packs", style="Question.TLabel").grid(row=0, column=0, sticky="w")
        filters = ttk.Frame(library_card, style="Card.TFrame")
        filters.grid(row=1, column=0, sticky="ew", pady=(10, 12))
        filters.columnconfigure(0, weight=1)

        self.library_search = ttk.Entry(filters, font=("Segoe UI", 10))
        self.library_search.grid(row=0, column=0, sticky="ew")
        self.library_search.bind("<KeyRelease>", lambda _event: self._schedule_library_search())

        filter_grid = ttk.Frame(filters, style="Card.TFrame")
        filter_grid.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        for column in range(3):
            filter_grid.columnconfigure(column, weight=1)

        ttk.Label(filter_grid, text="Category", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(filter_grid, text="Pack", style="Section.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Label(filter_grid, text="Focus", style="Section.TLabel").grid(row=0, column=2, sticky="w", padx=(8, 0))

        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(filter_grid, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.category_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_library_results())

        self.pack_var = tk.StringVar(value="All")
        self.pack_combo = ttk.Combobox(filter_grid, textvariable=self.pack_var, state="readonly")
        self.pack_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))
        self.pack_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_library_results())

        self.subcategory_var = tk.StringVar(value="All")
        self.subcategory_combo = ttk.Combobox(filter_grid, textvariable=self.subcategory_var, state="readonly")
        self.subcategory_combo.grid(row=1, column=2, sticky="ew", padx=(8, 0), pady=(6, 0))
        self.subcategory_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_library_results())

        utility_grid = ttk.Frame(filters, style="Card.TFrame")
        utility_grid.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        for column in range(3):
            utility_grid.columnconfigure(column, weight=1)

        ttk.Label(utility_grid, text="Domain", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(utility_grid, text="Audience", style="Section.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.domain_var = tk.StringVar(value="All")
        self.domain_combo = ttk.Combobox(utility_grid, textvariable=self.domain_var, state="readonly")
        self.domain_combo.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.domain_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_library_results())

        self.interest_var = tk.StringVar(value="All")
        self.interest_combo = ttk.Combobox(utility_grid, textvariable=self.interest_var, state="readonly")
        self.interest_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))
        self.interest_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_library_results())

        library_actions = ttk.Frame(utility_grid, style="Card.TFrame")
        library_actions.grid(row=0, column=2, rowspan=2, sticky="e", padx=(10, 0))
        self.refresh_library_button = ttk.Button(
            library_actions,
            text="Import Library",
            style="Secondary.TButton",
            command=self.refresh_web_library,
        )
        self.refresh_library_button.grid(row=0, column=0, sticky="e")
        self.reset_library_button = ttk.Button(
            library_actions,
            text="Reset Filters",
            style="Secondary.TButton",
            command=self.reset_library_filters,
        )
        self.reset_library_button.grid(row=1, column=0, sticky="e", pady=(8, 0))

        self.library_list = tk.Listbox(
            library_card,
            height=8,
            font=("Segoe UI", 10),
            bd=0,
            bg="#ffffff",
            fg="#211a15",
            activestyle="none",
        )
        library_list_shell = ttk.Frame(library_card, style="Card.TFrame")
        library_list_shell.grid(row=2, column=0, sticky="nsew")
        library_list_shell.columnconfigure(0, weight=1)
        library_list_shell.rowconfigure(0, weight=1)
        self.library_list.grid(in_=library_list_shell, row=0, column=0, sticky="nsew")
        library_list_scroll = ttk.Scrollbar(library_list_shell, orient="vertical", command=self.library_list.yview)
        library_list_scroll.grid(row=0, column=1, sticky="ns")
        self.library_list.configure(yscrollcommand=library_list_scroll.set)
        self.library_list.bind("<<ListboxSelect>>", lambda _event: self._show_selected_library())

        ttk.Label(library_card, text="Selected template preview", style="Section.TLabel").grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.library_preview = tk.Text(
            library_card,
            height=10,
            wrap="word",
            font=("Segoe UI", 10),
            bd=0,
            bg="#ffffff",
            fg="#211a15",
            padx=10,
            pady=10,
        )
        library_preview_shell = ttk.Frame(library_card, style="Card.TFrame")
        library_preview_shell.grid(row=4, column=0, sticky="nsew", pady=(8, 0))
        library_preview_shell.columnconfigure(0, weight=1)
        library_preview_shell.rowconfigure(0, weight=1)
        self.library_preview.grid(in_=library_preview_shell, row=0, column=0, sticky="nsew")
        library_preview_scroll = ttk.Scrollbar(library_preview_shell, orient="vertical", command=self.library_preview.yview)
        library_preview_scroll.grid(row=0, column=1, sticky="ns")
        self.library_preview.configure(yscrollcommand=library_preview_scroll.set)

        library_actions = ttk.Frame(library_card, style="Card.TFrame")
        library_actions.grid(row=5, column=0, sticky="ew", pady=(12, 0))
        ttk.Button(library_actions, text="Use Selected Prompt", style="Primary.TButton", command=self.load_selected_library).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(library_actions, text="Refresh Results", style="Secondary.TButton", command=self.refresh_library_results).grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )

    def _build_result_card(self, parent: ttk.Frame) -> None:
        result_card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        result_card.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(14, 0))
        result_card.columnconfigure(0, weight=1)
        result_card.rowconfigure(5, weight=1)
        result_card.rowconfigure(6, weight=3)
        self.result_card = result_card

        ttk.Label(result_card, text="Structured prompt output", style="Question.TLabel").grid(row=0, column=0, sticky="w")

        score_row = ttk.Frame(result_card, style="Card.TFrame")
        score_row.grid(row=1, column=0, sticky="ew", pady=(10, 8))
        score_row.columnconfigure(1, weight=1)
        self.score_label = ttk.Label(score_row, text="Prompt health: waiting", style="Question.TLabel")
        self.score_label.grid(row=0, column=0, sticky="w")
        self.result_mode_label = ttk.Label(score_row, text="Guided build", style="Section.TLabel")
        self.result_mode_label.grid(row=0, column=1, sticky="e")

        self.health_progress = ttk.Progressbar(result_card, mode="determinate", maximum=100, length=380)
        self.health_progress.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.health_summary = ttk.Label(
            result_card,
            text="Prompt health will appear here before the builder starts repairing it.",
            style="Muted.TLabel",
            wraplength=720,
            justify="left",
        )
        self.health_summary.grid(row=3, column=0, sticky="w", pady=(0, 12))

        self.loading_frame = ttk.Frame(result_card, style="Card.TFrame")
        self.loading_frame.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        self.loading_frame.columnconfigure(1, weight=1)
        self.loading_label = ttk.Label(self.loading_frame, text="", style="Section.TLabel")
        self.loading_label.grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.loading_progress = ttk.Progressbar(self.loading_frame, mode="indeterminate", length=200)
        self.loading_progress.grid(row=0, column=1, sticky="ew")
        self.loading_frame.grid_remove()

        self.why_improved = tk.Text(
            result_card,
            height=8,
            wrap="word",
            font=("Segoe UI", 10),
            bd=0,
            bg="#fbf5ed",
            fg="#4a3e32",
            padx=12,
            pady=12,
        )
        why_shell = ttk.Frame(result_card, style="Card.TFrame")
        why_shell.grid(row=5, column=0, sticky="nsew", pady=(0, 12))
        why_shell.columnconfigure(0, weight=1)
        why_shell.rowconfigure(0, weight=1)
        self.why_improved.grid(in_=why_shell, row=0, column=0, sticky="nsew")
        why_scroll = ttk.Scrollbar(why_shell, orient="vertical", command=self.why_improved.yview)
        why_scroll.grid(row=0, column=1, sticky="ns")
        self.why_improved.configure(yscrollcommand=why_scroll.set)
        self.why_improved.insert(
            "1.0",
            "Why this improved\n\n"
            "- Your prompt score will appear here after the first build.\n"
            "- The app will explain what it clarified and what is still missing.",
        )

        self.result_output = tk.Text(
            result_card,
            height=18,
            wrap="word",
            font=("Segoe UI", 11),
            bd=0,
            bg="#ffffff",
            fg="#211a15",
            padx=12,
            pady=12,
        )
        result_output_shell = ttk.Frame(result_card, style="Card.TFrame")
        result_output_shell.grid(row=6, column=0, sticky="nsew", pady=(0, 12))
        result_output_shell.columnconfigure(0, weight=1)
        result_output_shell.rowconfigure(0, weight=1)
        self.result_output.grid(in_=result_output_shell, row=0, column=0, sticky="nsew")
        result_output_scroll = ttk.Scrollbar(result_output_shell, orient="vertical", command=self.result_output.yview)
        result_output_scroll.grid(row=0, column=1, sticky="ns")
        self.result_output.configure(yscrollcommand=result_output_scroll.set)

        footer = ttk.Frame(result_card, style="Card.TFrame")
        footer.grid(row=7, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(footer, text="Ready. Type one rough idea, then click Analyze Prompt.", style="Muted.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w")
        self.copy_button = ttk.Button(footer, text="Copy", style="Secondary.TButton", command=self.copy_output)
        self.copy_button.grid(row=0, column=1, sticky="e")
        self.save_button = ttk.Button(footer, text="Save", style="Secondary.TButton", command=self.save_output)
        self.save_button.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.new_button = ttk.Button(footer, text="New", style="Secondary.TButton", command=self.reset_flow)
        self.new_button.grid(row=0, column=3, sticky="e", padx=(8, 0))

    def start_guided_flow(self) -> None:
        raw_prompt = self.quick_prompt_var.get().strip()
        if not raw_prompt:
            raw_prompt = self.prompt_input.get("1.0", "end").strip()
        if not raw_prompt:
            messagebox.showinfo("Prompt Assistant", "Start with at least one rough line.")
            return

        self.session = DesktopSession(task=raw_prompt)
        self.question_index = 0
        self.current_result = None
        self.current_inspection = None
        self.current_recommendation = None
        self.question_flow_active = False
        self.current_question_flow = QUESTION_FLOW_BY_MODE[self.mode_var.get()]
        self._set_question_controls_enabled(False)
        self.continue_button.configure(state="disabled", text="Open Repair Mode")
        self.apply_match_button.configure(state="disabled")
        self.coach_mode_badge.config(text=f"{self.mode_var.get()} mode")
        self.result_mode_label.config(text=f"{self.mode_var.get()} build")
        self.question_title.config(text="Checking prompt health...")
        self.question_hint.config(text="The app is looking for missing pieces, token waste, and the best pack match.")
        self._show_post_analysis_actions()
        self._run_background(
            status_text="Checking prompt health and matching the best pack...",
            work=lambda: self.assistant.inspect_prompt(
                prompt=raw_prompt,
                extra_context=self._combined_context_hint(),
                output_format=self.session.output_type,
                constraints=[],
            ),
            on_success=self._handle_prompt_inspection,
            on_error="The prompt could not be inspected right now.",
        )

    def _show_question(self) -> None:
        if self.question_index >= len(self.current_question_flow):
            self.question_flow_active = False
            self._set_question_controls_enabled(False)
            self.generate_structured_prompt()
            return
        field_name, question, hint = self.current_question_flow[self.question_index]
        existing = getattr(self.session, field_name, "")
        self.question_title.config(text=question)
        self.question_hint.config(text=hint)
        self.answer_entry.delete(0, "end")
        if existing:
            self.answer_entry.insert(0, existing)
        self._set_question_controls_enabled(True)
        self.answer_entry.focus_set()

    def next_question(self) -> None:
        if not self.question_flow_active or self.question_index >= len(self.current_question_flow):
            return
        field_name, _question, _hint = self.current_question_flow[self.question_index]
        setattr(self.session, field_name, self.answer_entry.get().strip())
        self.question_index += 1
        self._show_question()

    def skip_question(self) -> None:
        if not self.question_flow_active or self.question_index >= len(self.current_question_flow):
            return
        field_name, _question, _hint = self.current_question_flow[self.question_index]
        setattr(self.session, field_name, "")
        self.question_index += 1
        self._show_question()

    def open_advanced_context(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Context")
        dialog.configure(bg="#f3efe8")
        dialog.transient(self.root)
        self._center_child(dialog, 700, 540)

        frame = ttk.Frame(dialog, style="App.TFrame", padding=18)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Reference or file notes", style="Question.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            frame,
            text="Optional: add file notes, references, or patterns the final prompt should reuse.",
            style="Body.TLabel",
            wraplength=640,
        ).grid(row=1, column=0, sticky="w", pady=(6, 12))
        ttk.Label(
            frame,
            text="You can leave this window open and still type in the main prompt box.",
            style="Muted.TLabel",
            wraplength=640,
        ).grid(row=2, column=0, sticky="w", pady=(0, 12))

        ttk.Label(frame, text="Context files", style="Body.TLabel").grid(row=3, column=0, sticky="w")
        context_box = tk.Text(frame, height=5, wrap="word", font=("Segoe UI", 10), bd=0, bg="#ffffff", padx=10, pady=10)
        context_shell = ttk.Frame(frame, style="Card.TFrame")
        context_shell.grid(row=4, column=0, sticky="nsew", pady=(6, 12))
        context_shell.columnconfigure(0, weight=1)
        context_shell.rowconfigure(0, weight=1)
        context_box.grid(in_=context_shell, row=0, column=0, sticky="nsew")
        context_scroll = ttk.Scrollbar(context_shell, orient="vertical", command=context_box.yview)
        context_scroll.grid(row=0, column=1, sticky="ns")
        if self._context_files:
            context_box.insert("1.0", "\n".join(self._context_files))
        context_box.configure(yscrollcommand=context_scroll.set)

        ttk.Label(frame, text="Reference text", style="Body.TLabel").grid(row=5, column=0, sticky="w")
        reference_box = tk.Text(frame, height=6, wrap="word", font=("Segoe UI", 10), bd=0, bg="#ffffff", padx=10, pady=10)
        reference_shell = ttk.Frame(frame, style="Card.TFrame")
        reference_shell.grid(row=6, column=0, sticky="nsew", pady=(6, 12))
        reference_shell.columnconfigure(0, weight=1)
        reference_shell.rowconfigure(0, weight=1)
        reference_box.grid(in_=reference_shell, row=0, column=0, sticky="nsew")
        reference_scroll = ttk.Scrollbar(reference_shell, orient="vertical", command=reference_box.yview)
        reference_scroll.grid(row=0, column=1, sticky="ns")
        if self._reference_text:
            reference_box.insert("1.0", self._reference_text)
        reference_box.configure(yscrollcommand=reference_scroll.set)

        ttk.Label(frame, text="Reference patterns", style="Body.TLabel").grid(row=7, column=0, sticky="w")
        pattern_box = tk.Text(frame, height=5, wrap="word", font=("Segoe UI", 10), bd=0, bg="#ffffff", padx=10, pady=10)
        pattern_shell = ttk.Frame(frame, style="Card.TFrame")
        pattern_shell.grid(row=8, column=0, sticky="nsew", pady=(6, 12))
        pattern_shell.columnconfigure(0, weight=1)
        pattern_shell.rowconfigure(0, weight=1)
        pattern_box.grid(in_=pattern_shell, row=0, column=0, sticky="nsew")
        pattern_scroll = ttk.Scrollbar(pattern_shell, orient="vertical", command=pattern_box.yview)
        pattern_scroll.grid(row=0, column=1, sticky="ns")
        if self._reference_patterns:
            pattern_box.insert("1.0", "\n".join(self._reference_patterns))
        pattern_box.configure(yscrollcommand=pattern_scroll.set)
        frame.rowconfigure(8, weight=1)

        def save_advanced() -> None:
            self._context_files = [line.strip() for line in context_box.get("1.0", "end").splitlines() if line.strip()]
            self._reference_text = reference_box.get("1.0", "end").strip()
            self._reference_patterns = [line.strip() for line in pattern_box.get("1.0", "end").splitlines() if line.strip()]
            dialog.destroy()
            self.status_label.config(text="Advanced context saved for this session.")

        buttons = ttk.Frame(frame, style="App.TFrame")
        buttons.grid(row=9, column=0, sticky="e")
        ttk.Button(buttons, text="Cancel", style="Secondary.TButton", command=dialog.destroy).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Save Context", style="Primary.TButton", command=save_advanced).grid(row=0, column=1)

    def _combined_context_hint(self) -> str:
        parts = []
        if self._context_files:
            parts.append("Context files: " + "; ".join(self._context_files))
        if self._reference_text:
            parts.append(self._reference_text)
        if self._reference_patterns:
            parts.append("Reference patterns: " + "; ".join(self._reference_patterns))
        return " ".join(part for part in parts if part)

    def _handle_prompt_inspection(self, inspection) -> None:
        self.current_inspection = inspection
        analysis = inspection.analysis
        self._render_prompt_health(analysis)

        upgrade_ideas = suggest_prompt_upgrades(self.session.task)
        primary_suggestions = analysis.suggestions[:3]
        suggestion_lines = []
        suggestion_lines.extend(f"- {item}" for item in primary_suggestions)
        suggestion_lines.extend(f"- {item}" for item in upgrade_ideas if item not in primary_suggestions)
        self.suggestion_label.config(text="\n".join(suggestion_lines[:5]))

        if inspection.recommendations:
            top = inspection.recommendations[0]
            self.current_recommendation = top
            self.match_label.config(
                text=(
                    f"Best match: {top['title']} | {top['pack']} | {top['subcategory']}\n"
                    f"{top['reason']}. You can open Packs or let the builder repair the prompt first."
                )
            )
            self._apply_best_recommendation(top)
        else:
            self.current_recommendation = None
            self.match_label.config(
                text="No clear pack match yet. The builder will still help by tightening the prompt structure first."
            )

        self._prepare_repair_session(analysis, self.current_recommendation)

        if analysis.repair_mode:
            self.status_label.config(text=f"Repair mode is on. Prompt health is {analysis.score}/100, so the app will tighten the weak parts first.")
            self.question_title.config(text="Repair mode available. Review the diagnosis, then open repair mode when ready.")
            self.question_hint.config(text="The app has prepared pack-aware questions, but it will wait for your confirmation.")
            self.continue_button.configure(text="Open Repair Mode", state="normal")
        else:
            self.status_label.config(text=f"Prompt health is {analysis.score}/100. The prompt is usable, and the builder can still sharpen it.")
            self.question_title.config(text="Healthy prompt detected. You can still build a stronger version if you want.")
            self.question_hint.config(text="Use the builder for a sharper result, or load the best matching template first.")
            self.continue_button.configure(text="Build Prompt", state="normal")

        if inspection.recommendations:
            self.apply_match_button.configure(state="normal")

        self._render_prebuild_summary(analysis, inspection.recommendations)

    def _apply_best_recommendation(self, recommendation: dict) -> None:
        self.category_var.set(recommendation["category"])
        self.pack_var.set(recommendation["pack"])
        self.refresh_library_filters()
        available_subcategories = list(self.subcategory_combo["values"])
        self.subcategory_var.set(recommendation["subcategory"] if recommendation["subcategory"] in available_subcategories else "All")
        self.refresh_library_results()

    def enter_repair_mode(self) -> None:
        if not self.current_inspection:
            messagebox.showinfo("Prompt Assistant", "Analyze a prompt first so the app can prepare the repair flow.")
            return
        self.question_flow_active = True
        self.question_index = 0
        self.status_label.config(text="Repair flow started. Answer what matters and skip what does not.")
        self.question_title.config(text="Repair flow started.")
        self.question_hint.config(text="The next questions are based on your prompt health and the best matching pack.")
        self._show_question()

    def load_best_match(self) -> None:
        if not self.current_recommendation:
            messagebox.showinfo("Prompt Assistant", "Analyze a prompt first so the app can recommend a matching template.")
            return
        matched_prompt = self.current_recommendation.get("prompt_text", "")
        self._reference_text = matched_prompt
        self.quick_prompt_var.set(matched_prompt)
        self.prompt_input.delete("1.0", "end")
        self.prompt_input.insert("1.0", matched_prompt)
        self.status_label.config(
            text=f"Loaded the best match '{self.current_recommendation['title']}' into the prompt box."
        )

    def _show_selected_best_match(self) -> None:
        if not self.current_recommendation or not self._library_rows:
            return
        for index, prompt in enumerate(self._library_rows):
            if prompt.title == self.current_recommendation["title"] and prompt.pack == self.current_recommendation["pack"]:
                self.library_list.selection_clear(0, "end")
                self.library_list.selection_set(index)
                self.library_list.see(index)
                self._show_selected_library()
                return

    def _prepare_repair_session(self, analysis, recommendation: dict | None) -> None:
        if recommendation:
            self._apply_repair_defaults(recommendation)
        self.current_question_flow = self._build_repair_question_flow(analysis, recommendation)
        self.question_index = 0

    def _apply_repair_defaults(self, recommendation: dict) -> None:
        if not self.session.output_type:
            inferred_output = self._infer_output_type_from_recommendation(recommendation)
            if inferred_output:
                self.session.output_type = inferred_output
        if not self.session.tone and recommendation.get("repair_hints"):
            self.session.tone = "clear and practical"
        if not self.session.constraints_text and recommendation.get("common_missing_elements"):
            if "word limit" in [item.lower() for item in recommendation["common_missing_elements"]]:
                self.session.constraints_text = "Keep it concise."

    def _build_repair_question_flow(self, analysis, recommendation: dict | None) -> list[tuple[str, str, str]]:
        ordered_fields: list[str] = []
        missing_elements = []
        if recommendation:
            missing_elements.extend(recommendation.get("common_missing_elements", []))
            missing_elements.extend(recommendation.get("template_fields", []))

        for element in missing_elements:
            normalized = REPAIR_FIELD_ALIASES.get(str(element).strip().lower())
            if normalized and normalized not in ordered_fields:
                ordered_fields.append(normalized)

        gap_to_field = {
            "background or audience context": "recipient",
            "desired output format": "output_type",
            "constraints": "constraints_text",
        }
        for gap in analysis.gaps:
            lowered = gap.lower()
            for phrase, field in gap_to_field.items():
                if phrase in lowered and field not in ordered_fields:
                    ordered_fields.append(field)

        for field_name in ["goal", "recipient", "output_type", "desired_action", "avoid", "constraints_text", "success_criteria", "tone"]:
            if field_name not in ordered_fields:
                ordered_fields.append(field_name)

        if self.mode_var.get() == "Quick":
            ordered_fields = ordered_fields[:3]
        elif self.mode_var.get() == "Guided":
            ordered_fields = ordered_fields[:6]

        questions: list[tuple[str, str, str]] = []
        for field_name in ordered_fields:
            if field_name not in FIELD_PROMPTS:
                continue
            question, hint = FIELD_PROMPTS[field_name]
            if recommendation:
                question, hint = self._customize_question(field_name, question, hint, recommendation)
            questions.append((field_name, question, hint))
        return questions

    def _customize_question(self, field_name: str, question: str, hint: str, recommendation: dict) -> tuple[str, str]:
        pack = recommendation.get("pack", "")
        subcategory = recommendation.get("subcategory", "")
        if field_name == "output_type":
            question = f"What output shape would help most for this {subcategory.lower()} prompt?"
        elif field_name == "recipient":
            question = f"Who is the real audience for this {pack.lower()} prompt?"
        elif field_name == "goal":
            question = f"What should this {subcategory.lower()} prompt achieve when it works?"
        elif field_name == "desired_action":
            question = "What should the reader or user do next after seeing the result?"
        elif field_name == "constraints_text":
            question = f"What rules should keep this {pack.lower()} prompt focused?"

        repair_hints = recommendation.get("repair_hints", [])
        if repair_hints:
            hint = repair_hints[0] if field_name in {"goal", "recipient", "output_type"} else hint
        return question, hint

    def _infer_output_type_from_recommendation(self, recommendation: dict) -> str:
        subcategory = recommendation.get("subcategory", "").lower()
        pack = recommendation.get("pack", "").lower()
        if "email" in subcategory or "email" in pack:
            return "short email with subject line"
        if "proposal" in subcategory or "proposal" in pack:
            return "structured proposal"
        if "summary" in subcategory or "meeting" in pack:
            return "summary with decisions and next steps"
        if "study" in subcategory or "paper" in pack:
            return "study guide or bullet summary"
        if "bug" in pack or "code" in pack:
            return "step-by-step technical breakdown"
        if "story" in pack:
            return "structured outline"
        if "blog" in pack:
            return "outline with headings"
        return ""

    def _render_prompt_health(self, analysis) -> None:
        self.health_progress["value"] = analysis.score
        repair_text = "Repair Mode" if analysis.repair_mode else "Healthy Mode"
        self.score_label.config(text=f"Prompt health: {analysis.score}/100")
        risk_text = analysis.risk_flags[0] if analysis.risk_flags else "The prompt is in decent shape."
        self.health_summary.config(
            text=f"{analysis.health_label} | {repair_text}\nTop risk: {risk_text}"
        )

    def _render_prebuild_summary(self, analysis, recommendations: list[dict]) -> None:
        lines = ["Prompt diagnosis", ""]
        if analysis.gaps:
            lines.append("Missing or weak elements:")
            lines.extend(f"- {gap}" for gap in analysis.gaps[:4])
            lines.append("")
        if analysis.risk_flags:
            lines.append("Risk flags:")
            lines.extend(f"- {flag}" for flag in analysis.risk_flags[:3])
            lines.append("")
        if recommendations:
            top = recommendations[0]
            lines.append("Best matching template:")
            lines.append(f"- {top['title']} | {top['pack']} | {top['subcategory']}")
            lines.append(f"- {top['reason']}")
            if top.get("common_missing_elements"):
                lines.append(f"- Helps with: {', '.join(top['common_missing_elements'][:4])}")
            lines.append("- Next move: open repair mode, or use the best match template as your starting structure.")
        else:
            lines.append("No clear template match yet. The general repair flow can still strengthen the prompt.")
        self.why_improved.delete("1.0", "end")
        self.why_improved.insert("1.0", "\n".join(lines))

    def generate_structured_prompt(self) -> None:
        blueprint = GuidedPromptBlueprint(
            task=self.session.task,
            goal=self.session.goal,
            context_files=self._context_files,
            reference_text=self._build_reference_text_for_repair(),
            reference_patterns=self._reference_patterns,
            output_type=self.session.output_type,
            recipient=self.session.recipient,
            desired_action=self.session.desired_action,
            avoid=self.session.avoid,
            success_criteria=self.session.success_criteria or self.session.goal or "",
            tone=self.session.tone or "clear and practical",
        )
        if self.mode_var.get() == "Expert":
            blueprint.rules.extend(
                [
                    "List assumptions before execution.",
                    "Prefer more specific structure over generic output.",
                ]
            )
        if self.session.constraints_text.strip():
            blueprint.rules.extend(
                [item.strip() for item in self.session.constraints_text.replace("\n", ";").split(";") if item.strip()]
            )
        if self.current_recommendation:
            blueprint.rules.extend(self.current_recommendation.get("repair_hints", [])[:2])
        self._run_background(
            status_text="Building your structured prompt...",
            work=lambda: self.assistant.guide_prompt(blueprint=blueprint, save=True),
            on_success=self._handle_guided_result,
            on_error="The prompt could not be built right now.",
        )

    def _build_reference_text_for_repair(self) -> str:
        if self._reference_text.strip():
            return self._reference_text
        if not self.current_recommendation:
            return ""
        return (
            f"Use the structure style of the recommended template '{self.current_recommendation['title']}' "
            f"from the {self.current_recommendation['pack']}."
        )

    def refine_current_output(self) -> None:
        current_text = self.result_output.get("1.0", "end").strip()
        if not current_text:
            self.start_guided_flow()
            return
        self._run_background(
            status_text="Refining the structured prompt...",
            work=lambda: self.assistant.improve_prompt(
                prompt=current_text,
                extra_context="This is a previously structured prompt. Tighten it further without losing intent.",
                output_format="structured prompt",
                constraints=["Preserve the sectioned format."],
                tone=self.session.tone or "clear and practical",
                save=True,
            ),
            on_success=self._handle_refined_result,
            on_error="The prompt could not be refined right now.",
        )

    def copy_output(self) -> None:
        text = self.result_output.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Prompt Assistant", "There is nothing to copy yet.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status_label.config(text="Copied the structured prompt to your clipboard.")

    def save_output(self) -> None:
        text = self.result_output.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Prompt Assistant", "There is nothing to save yet.")
            return
        export_dir = self.assistant.settings.app_home / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        default_name = f"prompt-assistant-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        path = filedialog.asksaveasfilename(
            title="Save structured prompt",
            initialdir=str(export_dir),
            initialfile=default_name,
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
        )
        if not path:
            return
        Path(path).write_text(text, encoding="utf-8")
        self.status_label.config(text=f"Saved prompt to {path}.")

    def refresh_history_tab(self) -> None:
        self._history_rows = self.assistant.history_full(limit=20)
        self.history_list.delete(0, "end")
        for row in self._history_rows:
            label = f"#{row['id']}  {self._format_time(row['created_at'])}  {self._shorten(row['prompt'])}"
            self.history_list.insert("end", label)
        self.history_preview.delete("1.0", "end")
        if not self._history_rows:
            self.history_preview.insert("1.0", "No saved prompts yet. Your generated prompts will appear here.")

    def _show_selected_history(self) -> None:
        selection = self.history_list.curselection()
        if not selection:
            return
        row = self._history_rows[selection[0]]
        preview = (
            f"Original idea:\n{row['prompt']}\n\n"
            f"Improved prompt:\n{row['improved_prompt']}\n\n"
            f"Saved on: {self._format_time(row['created_at'])}"
        )
        self.history_preview.delete("1.0", "end")
        self.history_preview.insert("1.0", preview)

    def load_selected_history(self) -> None:
        selection = self.history_list.curselection()
        if not selection:
            messagebox.showinfo("Prompt Assistant", "Choose a saved prompt from history first.")
            return
        row = self._history_rows[selection[0]]
        self.quick_prompt_var.set(row["prompt"])
        self.prompt_input.delete("1.0", "end")
        self.prompt_input.insert("1.0", row["prompt"])
        self.result_output.delete("1.0", "end")
        self.result_output.insert("1.0", row["improved_prompt"])
        self.status_label.config(text="Loaded a past prompt back into the workspace.")

    def refresh_library_filters(self) -> None:
        self.category_combo["values"] = self.assistant.library.available_categories()
        self.pack_combo["values"] = self.assistant.library.available_packs(
            category=self.category_var.get() or "All"
        )
        self.subcategory_combo["values"] = self.assistant.library.available_subcategories(
            pack=self.pack_var.get() or "All",
            category=self.category_var.get() or "All",
        )
        self.domain_combo["values"] = self.assistant.library.available_domains()
        self.interest_combo["values"] = self.assistant.library.available_interests()
        if self.category_var.get() not in self.category_combo["values"]:
            self.category_var.set("All")
        if self.pack_var.get() not in self.pack_combo["values"]:
            self.pack_var.set("All")
        if self.subcategory_var.get() not in self.subcategory_combo["values"]:
            self.subcategory_var.set("All")
        if self.domain_var.get() not in self.domain_combo["values"]:
            self.domain_var.set("All")
        if self.interest_var.get() not in self.interest_combo["values"]:
            self.interest_var.set("All")

    def refresh_library_results(self) -> None:
        self.refresh_library_filters()
        self._library_rows = self.assistant.library.search(
            query=self.library_search.get().strip(),
            category=self.category_var.get() or "All",
            pack=self.pack_var.get() or "All",
            subcategory=self.subcategory_var.get() or "All",
            domain=self.domain_var.get() or "All",
            interest=self.interest_var.get() or "All",
        )
        self.library_list.delete(0, "end")
        for prompt in self._library_rows:
            category = self.assistant.library.category_for_pack(prompt.pack)
            label = f"{prompt.title}  [{category} / {prompt.pack} / {prompt.subcategory}]"
            self.library_list.insert("end", label)
        self.library_preview.delete("1.0", "end")
        if not self._library_rows:
            self.library_preview.insert(
                "1.0",
                "No prompt templates matched these filters yet.\n\nTry Reset Filters or choose a broader Category or Pack.",
            )

    def reset_library_filters(self) -> None:
        self.category_var.set("All")
        self.pack_var.set("All")
        self.subcategory_var.set("All")
        self.domain_var.set("All")
        self.interest_var.set("All")
        self.library_search.delete(0, "end")
        self.refresh_library_results()

    def _schedule_library_search(self) -> None:
        if self._library_search_after_id:
            self.root.after_cancel(self._library_search_after_id)
        self._library_search_after_id = self.root.after(180, self._run_scheduled_library_search)

    def _run_scheduled_library_search(self) -> None:
        self._library_search_after_id = None
        self.refresh_library_results()

    def _show_selected_library(self) -> None:
        selection = self.library_list.curselection()
        if not selection:
            return
        prompt = self._library_rows[selection[0]]
        template_fields = ", ".join(prompt.template_fields[:5]) if prompt.template_fields else "Not specified"
        missing_elements = ", ".join(prompt.common_missing_elements[:4]) if prompt.common_missing_elements else "Not specified"
        why_it_works = "\n".join(f"- {item}" for item in prompt.why_it_works[:3]) or "- Uses a stronger built-in structure."
        repair_hints = "\n".join(f"- {item}" for item in prompt.repair_hints[:3]) or "- No extra repair hints."
        preview = (
            f"{prompt.title}\n"
            f"Category: {self.assistant.library.category_for_pack(prompt.pack)}\n"
            f"Pack: {prompt.pack}\n"
            f"Focus: {prompt.subcategory}\n"
            f"{prompt.domain} / {prompt.interest}\n"
            f"Source: {prompt.source_label}\n\n"
            f"{prompt.summary}\n\n"
            f"Template fields: {template_fields}\n"
            f"Common missing elements this pack helps with: {missing_elements}\n\n"
            f"Why this template works:\n{why_it_works}\n\n"
            f"Repair hints:\n{repair_hints}\n\n"
            f"{self._shorten(prompt.prompt_text, limit=1100)}"
        )
        self.library_preview.delete("1.0", "end")
        self.library_preview.insert("1.0", preview)

    def load_selected_library(self) -> None:
        selection = self.library_list.curselection()
        if not selection:
            messagebox.showinfo("Prompt Assistant", "Choose a prompt from the library first.")
            return
        prompt = self._library_rows[selection[0]]
        self.quick_prompt_var.set(prompt.prompt_text)
        self.prompt_input.delete("1.0", "end")
        self.prompt_input.insert("1.0", prompt.prompt_text)
        self.status_label.config(text=f"Loaded '{prompt.title}' into the main prompt box.")

    def refresh_web_library(self) -> None:
        self._run_background(
            status_text="Refreshing the open-source prompt library...",
            work=self.assistant.library.refresh_remote_prompts,
            on_success=self._handle_library_refresh,
            on_error="The web prompt library could not refresh right now.",
        )

    def reset_flow(self) -> None:
        self.session = DesktopSession()
        self.question_index = 0
        self.current_result = None
        self.current_inspection = None
        self.current_recommendation = None
        self.current_question_flow = QUESTION_FLOW_BY_MODE[self.mode_var.get()]
        self.question_flow_active = False
        self._context_files = []
        self._reference_text = ""
        self._reference_patterns = []
        self.quick_prompt_var.set("")
        self.prompt_input.delete("1.0", "end")
        self.result_output.delete("1.0", "end")
        self.why_improved.delete("1.0", "end")
        self.answer_entry.delete(0, "end")
        self.question_title.config(text="Type a rough prompt, then click Analyze Prompt.")
        self.question_hint.config(text="")
        self._set_question_controls_enabled(False)
        self.suggestion_label.config(text="The assistant will suggest stronger prompt ideas here.")
        self.match_label.config(text="Best pack matches will appear here after the app checks your prompt health.")
        self.status_label.config(text="Ready for a new prompt.")
        self.continue_button.configure(text="Open Repair Mode", state="disabled")
        self.apply_match_button.configure(state="disabled")
        self.score_label.config(text="Prompt health: waiting")
        self.health_progress["value"] = 0
        self.health_summary.config(text="Prompt health will appear here before the builder starts repairing it.")
        self.result_mode_label.config(text=f"{self.mode_var.get()} build")
        self._set_minimal_launch_mode()
        self.why_improved.insert(
            "1.0",
            "Why this improved\n\n"
            "- Your prompt score will appear here after the first build.\n"
            "- The app will explain what it clarified and what is still missing.",
        )

    def _render_result_summary(self, result) -> None:
        delta = result.final_analysis.score - result.analysis.score
        direction = f"+{delta}" if delta >= 0 else str(delta)
        self.score_label.config(text=f"Prompt health: {result.analysis.score} -> {result.final_analysis.score} ({direction})")
        self.health_progress["value"] = result.final_analysis.score
        self.health_summary.config(
            text=(
                f"{result.analysis.health_label} -> {result.final_analysis.health_label}\n"
                f"Repair mode {'stayed on' if result.final_analysis.repair_mode else 'was cleared'} after the rebuild."
            )
        )

        reasons: list[str] = []
        if result.analysis.gaps:
            reasons.extend(f"- Fixed: {gap}" for gap in result.analysis.gaps[:3])
        if result.final_analysis.strengths:
            reasons.extend(f"- Added: {item}" for item in result.final_analysis.strengths[:3])
        if result.recommendations:
            top = result.recommendations[0]
            reasons.append(f"- Best-matched pack: {top['pack']} -> {top['subcategory']}.")
            if top.get("repair_hints"):
                reasons.append(f"- Pack hint used: {top['repair_hints'][0]}")
        if result.final_analysis.risk_flags:
            reasons.append(f"- Remaining watch-out: {result.final_analysis.risk_flags[0]}")
        if not reasons:
            reasons.append("- The prompt was tightened without changing your original intent.")
        reasons.append("")
        reasons.append("Next move:")
        reasons.append(f"- {self._next_step_hint()}")

        self.why_improved.delete("1.0", "end")
        self.why_improved.insert("1.0", "Why this improved\n\n" + "\n".join(reasons))

    def _handle_guided_result(self, result) -> None:
        self.current_result = result
        self.question_flow_active = False
        self._set_question_controls_enabled(False)
        self.result_output.delete("1.0", "end")
        self.result_output.insert("1.0", result.improved_prompt)
        self._render_result_summary(result)
        self.status_label.config(text=f"Built and saved. Score {result.analysis.score} -> {result.final_analysis.score}.")
        self.question_title.config(text="Structured prompt ready.")
        self.question_hint.config(text="Copy it, save it, or refine it again.")
        self.answer_entry.delete(0, "end")
        self.refresh_history_tab()

    def _handle_refined_result(self, result) -> None:
        self.current_result = result
        self.question_flow_active = False
        self._set_question_controls_enabled(False)
        self.result_output.delete("1.0", "end")
        self.result_output.insert("1.0", result.improved_prompt)
        self._render_result_summary(result)
        self.status_label.config(text=f"Refined again. Score {result.analysis.score} -> {result.final_analysis.score}.")
        self.refresh_history_tab()

    def _handle_library_refresh(self, total: int) -> None:
        self.refresh_library_filters()
        self.refresh_library_results()
        self.status_label.config(text=f"Refreshed {total} open-source prompts into the local library.")

    def _run_background(self, *, status_text: str, work, on_success, on_error: str) -> None:
        self._set_busy(True, status_text)

        def runner() -> None:
            try:
                result = work()
            except Exception as exc:  # noqa: BLE001
                self.root.after(0, lambda: self._handle_background_error(on_error, exc))
                return
            self.root.after(0, lambda: self._handle_background_success(on_success, result))

        threading.Thread(target=runner, daemon=True).start()

    def _handle_background_success(self, callback, result) -> None:
        self._set_busy(False)
        callback(result)

    def _handle_background_error(self, title: str, exc: Exception) -> None:
        self._set_busy(False)
        if "Voice capture" in title:
            messagebox.showinfo(
                "Prompt Assistant",
                f"{title}\n\n{exc}\n\nYou can still type your idea normally.",
            )
            self.status_label.config(text="Voice input was not available. You can type instead.")
            return
        if "web prompt library" in title.lower():
            messagebox.showinfo(
                "Prompt Assistant",
                f"{title}\n\n{exc}\n\nYour built-in prompt packs still work locally.",
            )
            self.status_label.config(text="Web library refresh did not complete.")
            return
        messagebox.showinfo("Prompt Assistant", f"{title}\n\n{exc}")
        self.status_label.config(text=title)

    def _set_busy(self, is_busy: bool, status_text: str | None = None) -> None:
        if is_busy:
            self._busy_count += 1
            self.root.config(cursor="watch")
            self.loading_frame.grid()
            self.loading_progress.start(10)
            if status_text:
                self.loading_label.config(text=status_text)
            if status_text:
                self.status_label.config(text=status_text)
        else:
            self._busy_count = max(0, self._busy_count - 1)
            if self._busy_count == 0:
                self.root.config(cursor="")
                self.loading_progress.stop()
                self.loading_label.config(text="")
                self.loading_frame.grid_remove()
        self._set_controls_enabled(self._busy_count == 0)
        if self._busy_count == 0:
            self._ensure_prompt_editable()

    def _set_question_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.answer_entry.configure(state=state)
        self.skip_button.configure(state=state)
        self.next_button.configure(state=state)

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        readonly_state = "readonly" if enabled else "disabled"
        for button in [
            getattr(self, "start_button", None),
            getattr(self, "context_button", None),
            getattr(self, "refine_button", None),
            getattr(self, "pack_picker_button", None),
            getattr(self, "continue_button", None),
            getattr(self, "apply_match_button", None),
            getattr(self, "copy_button", None),
            getattr(self, "save_button", None),
            getattr(self, "new_button", None),
            getattr(self, "refresh_library_button", None),
        ]:
            if button is not None:
                button.configure(state=state)
        self.library_search.configure(state=state)
        self.quick_prompt_entry.configure(state=state)
        self.category_combo.configure(state=readonly_state)
        self.pack_combo.configure(state=readonly_state)
        self.subcategory_combo.configure(state=readonly_state)
        self.domain_combo.configure(state=readonly_state)
        self.interest_combo.configure(state=readonly_state)
        self.prompt_input.configure(state=state)
        if not enabled:
            self._set_question_controls_enabled(False)

    def _next_step_hint(self) -> str:
        mode = self.mode_var.get()
        if mode == "Quick":
            return "If the result still feels broad, switch to Guided mode for a stronger brief."
        if mode == "Guided":
            return "If this is high-stakes, switch to Expert mode and add deeper context."
        return "Use Tighten Output only if you want a sharper version, not a different direction."

    def _load_ui_state(self) -> dict:
        if not self.ui_state_path.exists():
            return {}
        try:
            return json.loads(self.ui_state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _save_ui_state(self, payload: dict) -> None:
        self.ui_state_path.parent.mkdir(parents=True, exist_ok=True)
        self.ui_state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _maybe_show_first_run_picker(self) -> None:
        state = self._load_ui_state()
        if state.get("onboarding_complete"):
            return
        self.status_label.config(text="Tip: type a rough prompt to begin, or click Browse Starter Packs if you want a ready-made starting point.")

    def _focus_prompt_input(self) -> None:
        try:
            self.quick_prompt_entry.focus_set()
        except tk.TclError:
            return

    def _ensure_prompt_editable(self) -> None:
        try:
            self.prompt_input.configure(state="normal")
            self.quick_prompt_entry.configure(state="normal")
        except tk.TclError:
            return

    def _set_minimal_launch_mode(self) -> None:
        self.long_editor_label.grid_remove()
        self.prompt_input_shell.grid_remove()
        self.context_button.grid_remove()
        self.refine_button.grid_remove()
        self.continue_button.grid_remove()
        self.apply_match_button.grid_remove()
        self.question_title.config(text="Type a rough prompt, then click Analyze Prompt.")
        self.question_hint.config(text="You can browse a starter pack if you want help getting started.")

    def _show_post_analysis_actions(self) -> None:
        self.long_editor_label.grid()
        self.prompt_input_shell.grid()
        self.context_button.grid()
        self.refine_button.grid()
        self.continue_button.grid()
        self.apply_match_button.grid()

    def open_pack_picker(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose a Prompt Pack")
        dialog.configure(bg="#f3efe8")
        dialog.transient(self.root)
        self._center_child(dialog, 920, 720)

        outer = ttk.Frame(dialog, style="App.TFrame")
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg="#f3efe8", highlightthickness=0, bd=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = ttk.Frame(canvas, style="App.TFrame", padding=22)
        welcome_window = canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(welcome_window, width=event.width))
        canvas.bind_all("<MouseWheel>", lambda event, c=canvas: self._on_canvas_mousewheel(event, c))
        dialog.bind(
            "<Destroy>",
            lambda _event: self.main_canvas.bind_all("<MouseWheel>", self._on_main_mousewheel),
        )
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Start with a prompt pack", style="Question.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            frame,
            text="Pick the kind of work you want to do. The app will load a stronger starter prompt, the right mode, and the most relevant pack.",
            style="Body.TLabel",
            wraplength=740,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 16))

        category_modes = {
            "Writing & Content": "Guided",
            "Business & Strategy": "Expert",
            "Coding & Technical": "Expert",
            "Learning & Research": "Guided",
            "Creative & General": "Guided",
        }
        options = []
        for pack in PACK_CATALOG:
            first_template = pack["templates"][0]
            options.append(
                (
                    pack["category"],
                    pack["pack"],
                    first_template["subcategory"],
                    category_modes.get(pack["category"], "Guided"),
                    first_template["prompt_text"],
                    pack["use_case"],
                )
            )

        for index, (label, pack, subcategory, mode, prompt_text, description) in enumerate(options):
            row = 2 + index // 2
            column = index % 2
            card = ttk.Frame(frame, style="Card.TFrame", padding=14)
            card.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column == 0 else 0), pady=(0, 10))
            card.columnconfigure(0, weight=1)
            ttk.Label(card, text=label, style="Question.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(card, text=f"{pack} | {mode}", style="Section.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 6))
            ttk.Label(card, text=f"Focus: {subcategory}", style="Muted.TLabel", wraplength=320).grid(row=2, column=0, sticky="w")
            ttk.Label(card, text=description, style="Muted.TLabel", wraplength=320, justify="left").grid(row=3, column=0, sticky="w", pady=(6, 10))
            ttk.Button(
                card,
                text="Start Here",
                style="Primary.TButton",
                command=lambda p=pack, s=subcategory, m=mode, text=prompt_text, win=dialog: self._apply_onboarding_choice(p, s, m, text, win),
            ).grid(row=4, column=0, sticky="w")

        footer = ttk.Frame(frame, style="App.TFrame")
        footer_row = 2 + ((len(options) - 1) // 2) + 1
        footer.grid(row=footer_row, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(
            footer,
            text="Skip for now",
            style="Secondary.TButton",
            command=lambda: self._close_pack_picker_without_choice(dialog),
        ).grid(row=0, column=0, sticky="w")

    def _apply_onboarding_choice(
        self,
        pack: str,
        subcategory: str,
        mode: str,
        prompt_text: str,
        dialog: tk.Toplevel,
    ) -> None:
        self.mode_var.set(mode)
        self._on_mode_changed()
        self.category_var.set(self.assistant.library.category_for_pack(pack))
        self.pack_var.set(pack)
        self.refresh_library_filters()
        available_subcategories = list(self.subcategory_combo["values"])
        self.subcategory_var.set(subcategory if subcategory in available_subcategories else "All")
        self.refresh_library_results()
        self.prompt_input.configure(state="normal")
        self.prompt_input.delete("1.0", "end")
        self.prompt_input.insert("1.0", prompt_text)
        self.quick_prompt_var.set(prompt_text)
        self.status_label.config(text=f"Prompt pack loaded: {pack}.")
        self._save_ui_state(
            {
                "onboarding_complete": True,
                "preferred_category": self.assistant.library.category_for_pack(pack),
                "preferred_pack": pack,
                "preferred_mode": mode,
            }
        )
        dialog.destroy()

    def _close_pack_picker_without_choice(self, dialog: tk.Toplevel) -> None:
        state = self._load_ui_state()
        state["onboarding_complete"] = True
        self._save_ui_state(state)
        dialog.destroy()

    def _on_mode_changed(self) -> None:
        mode = self.mode_var.get()
        self.current_question_flow = QUESTION_FLOW_BY_MODE[mode]
        if hasattr(self, "mode_hint"):
            self.mode_hint.config(text=MODE_DESCRIPTIONS[mode])
        if hasattr(self, "coach_mode_badge"):
            self.coach_mode_badge.config(text=f"{mode} mode")
        if hasattr(self, "result_mode_label"):
            self.result_mode_label.config(text=f"{mode} build")

    def _on_main_mousewheel(self, event) -> None:
        self._on_canvas_mousewheel(event, self.main_canvas)

    def _on_canvas_mousewheel(self, event, canvas: tk.Canvas) -> None:
        try:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            return

    def _format_time(self, value: str) -> str:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.strftime("%d %b %H:%M")
        except ValueError:
            return value

    def _shorten(self, text: str, limit: int = 70) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."

    def _center_window(self, width: int, height: int) -> None:
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _center_child(self, window: tk.Toplevel, width: int, height: int) -> None:
        self.root.update_idletasks()
        x = self.root.winfo_x() + int((self.root.winfo_width() - width) / 2)
        y = self.root.winfo_y() + int((self.root.winfo_height() - height) / 2)
        window.geometry(f"{width}x{height}+{x}+{y}")


def run_desktop_app(assistant: PromptAssistant) -> None:
    PromptAssistantApp(assistant).run()
