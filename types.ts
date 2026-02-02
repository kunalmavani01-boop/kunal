
export interface Project {
  title: string;
  role: string;
  platform?: string;
  link?: string;
  description?: string;
  category: 'Non-Fiction' | 'Documentary' | 'Commercial' | 'Sports' | 'Fiction';
}

export interface Experience {
  company: string;
  role: string;
  period: string;
  projects: Project[];
}

export interface Education {
  degree: string;
  institution: string;
  year: string;
  specialization: string;
}

export interface ResumeData {
  name: string;
  headline: string;
  summary: string;
  email: string;
  phone: string;
  location: string;
  portfolio: string;
  competencies: string[];
  education: Education[];
  skills: {
    technical: string[];
    creative: string[];
    leadership: string[];
  };
  featuredProjects: Project[];
  allProjects: Project[];
}
