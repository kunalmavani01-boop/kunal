import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	JinaScrapeWebsiteTool,
	FileReadTool,
	SerperDevTool,
	ArxivPaperTool
)






@CrewBase
class Project360DegreeAiPromptAssistantPlatformCrew:
    """Project360DegreeAiPromptAssistantPlatform crew"""

    
    @agent
    def senior_project_manager(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["senior_project_manager"],
            
            
            tools=[				JinaScrapeWebsiteTool(),
				FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def backend_python_engineer(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["backend_python_engineer"],
            
            
            tools=[				FileReadTool(),
				JinaScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def python_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["python_engineer"],
            tools=[FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
            ),
        )

    
    @agent
    def frontend_engineer(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["frontend_engineer"],
            
            
            tools=[				FileReadTool(),
				SerperDevTool(),
				JinaScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def release_program_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["release_program_manager"],
            tools=[FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
            ),
        )

    
    @agent
    def windows_packaging_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["windows_packaging_engineer"],
            tools=[FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
            ),
        )

    
    @agent
    def macos_release_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["macos_release_planner"],
            tools=[FileReadTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
            ),
        )

    
    @agent
    def r_d_market_scout(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["r_d_market_scout"],
            
            
            tools=[				SerperDevTool(),
				JinaScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def ai_prompt_engineering_researcher(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["ai_prompt_engineering_researcher"],
            
            
            tools=[				SerperDevTool(),
				ArxivPaperTool(),
				JinaScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    
    @agent
    def legal_ip_compliance_lead(self) -> Agent:
        
        
        return Agent(
            config=self.agents_config["legal_ip_compliance_lead"],
            
            
            tools=[				SerperDevTool(),
				JinaScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=LLM(
                model="openai/gpt-4o-mini",
                
                
            ),
            
        )
        
    

    
    @task
    def cli_core_architecture(self) -> Task:
        return Task(
            config=self.tasks_config["cli_core_architecture"],
            markdown=False,
            
            
        )
    
    @task
    def local_first_memory_store(self) -> Task:
        return Task(
            config=self.tasks_config["local_first_memory_store"],
            markdown=False,
            
            
        )
    
    @task
    def optimization_engine_logic(self) -> Task:
        return Task(
            config=self.tasks_config["optimization_engine_logic"],
            markdown=False,
            
            
        )
    
    @task
    def privacy_audit_legal_framework(self) -> Task:
        return Task(
            config=self.tasks_config["privacy_audit_legal_framework"],
            markdown=False,
            
            
        )
    
    @task
    def adaptive_learning_loop(self) -> Task:
        return Task(
            config=self.tasks_config["adaptive_learning_loop"],
            markdown=False,
            
            
        )
    
    @task
    def python_quality_audit(self) -> Task:
        return Task(
            config=self.tasks_config["python_quality_audit"],
            markdown=False,
        )

    @task
    def backend_beta_stabilization(self) -> Task:
        return Task(
            config=self.tasks_config["backend_beta_stabilization"],
            markdown=False,
        )

    @task
    def frontend_beta_experience(self) -> Task:
        return Task(
            config=self.tasks_config["frontend_beta_experience"],
            markdown=False,
        )

    @task
    def release_readiness_audit(self) -> Task:
        return Task(
            config=self.tasks_config["release_readiness_audit"],
            markdown=False,
        )

    @task
    def windows_exe_packaging(self) -> Task:
        return Task(
            config=self.tasks_config["windows_exe_packaging"],
            markdown=False,
        )

    @task
    def macos_dmg_release_plan(self) -> Task:
        return Task(
            config=self.tasks_config["macos_dmg_release_plan"],
            markdown=False,
        )

    @task
    def strategic_intelligence_report(self) -> Task:
        return Task(
            config=self.tasks_config["strategic_intelligence_report"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the Project360DegreeAiPromptAssistantPlatform crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,

            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )
