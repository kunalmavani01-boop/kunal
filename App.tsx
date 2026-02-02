
import React, { useState, useEffect } from 'react';
import { 
  Mail, Phone, MapPin, Globe, Award, Briefcase, 
  GraduationCap, ChevronRight, Layout, Printer, 
  Share2, ExternalLink, Download, ArrowUpRight, 
  Clapperboard, MonitorPlay, Film, Radio, Sparkles,
  Camera, Layers, Users, FileText, Zap, Rocket, Star, Target,
  Eye, Command, Pocket, Box, CheckCircle, X
} from 'lucide-react';
import { resumeData } from './data';
import { Project } from './types';
import * as docx from 'docx';
import FileSaver from 'file-saver';

const App: React.FC = () => {
  const [filter, setFilter] = useState<string>('All');
  const [scrolled, setScrolled] = useState(false);
  const [isGeneratingWord, setIsGeneratingWord] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [copiedLink, setCopiedLink] = useState<string | null>(null);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (selectedProject) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
  }, [selectedProject]);

  const handlePrint = () => {
    window.print();
  };

  const handleCopyLink = (link: string, id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(link);
    setCopiedLink(id);
    setTimeout(() => setCopiedLink(null), 2000);
  };

  const handleDownloadWord = async () => {
    setIsGeneratingWord(true);
    try {
      const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = docx;
      const doc = new Document({
        sections: [{
          properties: {},
          children: [
            new Paragraph({
              text: resumeData.name,
              heading: HeadingLevel.HEADING_1,
              alignment: AlignmentType.CENTER,
            }),
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: resumeData.headline, bold: true, color: "4F46E5", size: 28 }),
              ],
            }),
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: `${resumeData.email} | ${resumeData.phone} | ${resumeData.location}` }),
              ],
              spacing: { after: 300 }
            }),
            new Paragraph({ text: "PROFESSIONAL PROFILE", heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: resumeData.summary, spacing: { after: 200 } }),
            new Paragraph({ text: "STRENGTHS & SKILLS", heading: HeadingLevel.HEADING_2 }),
            ...resumeData.competencies.map(c => new Paragraph({ text: c, bullet: { level: 0 } })),
            new Paragraph({ text: "PROJECT ARCHIVE", heading: HeadingLevel.HEADING_2, spacing: { before: 300 } }),
            ...resumeData.allProjects.map(p => new Paragraph({ 
              children: [
                new TextRun({ text: p.title, bold: true }),
                new TextRun({ text: ` (${p.role}) - ${p.category}` }),
                p.link ? new TextRun({ text: ` | Link: ${p.link}`, color: "4F46E5" }) : new TextRun({ text: "" })
              ],
              spacing: { after: 100 }
            }))
          ],
        }],
      });
      const blob = await Packer.toBlob(doc);
      FileSaver.saveAs(blob, `${resumeData.name.replace(/\s+/g, '_')}_Professional_Resume.docx`);
    } catch (error) {
      console.error("Error generating Word document:", error);
      alert("There was an issue generating the Word document. Please try the PDF option.");
    } finally {
      setIsGeneratingWord(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch(category) {
      case 'Fiction': return <Film size={20} />;
      case 'Documentary': return <Clapperboard size={20} />;
      case 'Commercial': return <Sparkles size={20} />;
      case 'Sports': return <Radio size={20} />;
      default: return <MonitorPlay size={20} />;
    }
  };

  return (
    <div id="resume-content" className="min-h-screen bg-[#050505] text-slate-200 selection:bg-indigo-500/30">
      {/* Enhanced Cinematic Scanline Overlay */}
      <div className="scanline-container no-print">
        <div className="scanline-static" />
        <div className="scanline-moving" />
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-500 no-print ${
        scrolled ? 'bg-black/95 backdrop-blur-2xl border-b border-white/5 py-3' : 'bg-transparent py-4 md:py-8'
      }`}>
        <div className="max-w-[1400px] mx-auto px-6 md:px-10 flex items-center justify-between">
          <div className="flex items-center gap-4 group cursor-pointer" onClick={() => window.scrollTo({top: 0, behavior: 'smooth'})}>
            <span className="serif-noir italic text-2xl font-bold tracking-tighter text-white">KM</span>
            <div className="hidden sm:block h-4 w-px bg-white/10 mx-1" />
            <span className="hidden sm:block text-[9px] font-black tracking-[0.4em] text-slate-500 uppercase">Director & Creative Director</span>
          </div>
          
          <div className="flex items-center gap-4 md:gap-8">
            <button 
              onClick={handleDownloadWord}
              disabled={isGeneratingWord}
              className="group flex items-center gap-2 text-[10px] font-black tracking-[0.2em] uppercase text-slate-500 hover:text-white transition-colors disabled:opacity-30 hidden md:flex"
            >
              <FileText size={14} />
              <span>{isGeneratingWord ? '...' : 'DOCX'}</span>
            </button>
            <button 
              onClick={handlePrint}
              className="group flex items-center gap-2 md:gap-3 bg-white text-black px-5 md:px-8 py-2 md:py-2.5 rounded-full text-[9px] md:text-[10px] font-black tracking-[0.2em] uppercase hover:bg-indigo-600 hover:text-white transition-all active:scale-95 shadow-xl shadow-white/5"
            >
              <Download size={14} />
              <span>Save PDF</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[70vh] md:h-[85vh] flex items-center overflow-hidden border-b border-white/5 print:h-auto print:border-black">
        <div className="absolute inset-0 z-0 bg-gradient-to-b from-indigo-950/20 via-[#050505] to-[#050505] print:hidden"></div>

        <div className="relative z-10 max-w-[1400px] mx-auto px-6 md:px-10 w-full pt-28 md:pt-20 pb-12">
          <div className="max-w-4xl space-y-6 md:space-y-8 animate-fade-in">
            <h1 className="text-6xl md:text-8xl lg:text-[10rem] leading-[0.8] font-black serif-noir text-white tracking-tighter italic print:text-black">
              {resumeData.name}.
            </h1>
            <h2 className="text-sm md:text-xl font-black tracking-[0.3em] md:tracking-[0.5em] text-indigo-500 uppercase">{resumeData.headline}</h2>
            <p className="text-lg md:text-2xl text-slate-400 font-light leading-relaxed max-w-2xl serif-noir italic print:text-gray-700">
              "A professional with over 14 years of experience, committed to delivering quality through a sincere and adaptive approach to production."
            </p>
            <div className="flex flex-col sm:flex-row flex-wrap gap-6 md:gap-10 pt-4 print:text-black">
              <div className="space-y-1">
                <span className="text-[9px] font-black tracking-[0.3em] uppercase text-slate-600 print:text-gray-500">Contact</span>
                <p className="text-base md:text-lg font-bold text-slate-300 print:text-black">{resumeData.phone}</p>
              </div>
              <div className="space-y-1">
                <span className="text-[9px] font-black tracking-[0.3em] uppercase text-slate-600 print:text-gray-500">Base</span>
                <p className="text-base md:text-lg font-bold text-slate-300 print:text-black">{resumeData.location}</p>
              </div>
              <div className="space-y-1">
                <span className="text-[9px] font-black tracking-[0.3em] uppercase text-slate-600 print:text-gray-500">Email</span>
                <p className="text-base md:text-lg font-bold text-slate-300 print:text-black break-all">{resumeData.email}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Profile & Skills */}
      <section className="py-20 md:py-32 bg-zinc-950 print:bg-white print:py-8">
        <div className="max-w-[1400px] mx-auto px-6 md:px-10">
          <div className="grid lg:grid-cols-2 gap-12 md:gap-24 items-start print:gap-12">
            <div className="space-y-8 md:space-y-12 print:space-y-6">
              <div className="space-y-6">
                <h2 className="text-[10px] font-black tracking-[0.6em] text-indigo-500 uppercase flex items-center gap-3">
                  <Command size={14} /> Professional Approach
                </h2>
                <h3 className="text-4xl md:text-5xl font-bold serif-noir tracking-tight text-white leading-tight print:text-black">
                  Sincere, Diligent & Team Oriented.
                </h3>
                <p className="text-base md:text-lg text-slate-500 font-light leading-relaxed print:text-gray-700">
                  {resumeData.summary}
                </p>
                <div className="space-y-4 md:space-y-6 pt-4">
                  <div className="flex items-start gap-4">
                    <CheckCircle className="text-indigo-500 mt-1 shrink-0" size={18} />
                    <p className="text-slate-400 text-sm print:text-gray-600">"A groomed professional with a hands-on attitude, willing to adapt to changing work environments."</p>
                  </div>
                  <div className="flex items-start gap-4">
                    <CheckCircle className="text-indigo-500 mt-1 shrink-0" size={18} />
                    <p className="text-slate-400 text-sm print:text-gray-600">"Well organized with a record of self-motivation and creative initiative to achieve personal and corporate goals."</p>
                  </div>
                  <div className="flex items-start gap-4">
                    <CheckCircle className="text-indigo-500 mt-1 shrink-0" size={18} />
                    <p className="text-slate-400 text-sm print:text-gray-600">"Literate with the complete range of duties from conceptualization and planning to post-production execution."</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-6 md:gap-8 print:gap-4">
              <div className="glass-noir p-6 md:p-10 rounded-3xl md:rounded-[2rem] border border-white/5 space-y-6 print:border-gray-200 print:rounded-lg print:p-6">
                <h4 className="text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase">Core Strengths</h4>
                <ul className="space-y-3 md:space-y-4">
                  {resumeData.competencies.map((c, i) => (
                    <li key={i} className="text-slate-400 text-xs md:text-sm font-medium flex items-center gap-3 print:text-black">
                      <span className="w-1 h-1 bg-indigo-500 rounded-full shrink-0" /> {c}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="glass-noir p-6 md:p-10 rounded-3xl md:rounded-[2rem] border border-white/5 space-y-6 print:border-gray-200 print:rounded-lg print:p-6">
                <h4 className="text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase">Key Technicals</h4>
                <ul className="space-y-3 md:space-y-4">
                  {resumeData.skills.technical.map((s, i) => (
                    <li key={i} className="text-slate-400 text-xs md:text-sm font-medium flex items-center gap-3 print:text-black">
                      <span className="w-1 h-1 bg-indigo-500 rounded-full shrink-0" /> {s}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Works */}
      <section className="py-20 md:py-32 bg-[#050505] print:bg-white print:py-8">
        <div className="max-w-[1400px] mx-auto px-6 md:px-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 mb-16 md:mb-24 print:mb-8">
            <div className="space-y-4">
              <h2 className="text-[10px] font-black tracking-[0.6em] text-indigo-500 uppercase">Selected Portfolio</h2>
              <h3 className="text-5xl md:text-6xl font-black serif-noir text-white tracking-tighter italic print:text-black">Career Highlights.</h3>
            </div>
            <a href={resumeData.portfolio} target="_blank" className="flex items-center justify-center gap-3 px-8 py-3.5 glass-noir rounded-full text-[9px] font-black tracking-[0.3em] uppercase hover:bg-white hover:text-black transition-all no-print w-full md:w-auto">
              Full Portfolio Archive <ArrowUpRight size={16} />
            </a>
          </div>

          <div className="grid lg:grid-cols-2 gap-8 md:gap-12 print:gap-8">
            {resumeData.featuredProjects.map((p, i) => (
              <div key={i} className="group glass-noir p-8 md:p-12 rounded-[2rem] md:rounded-[2.5rem] border border-white/5 flex flex-col justify-between hover:border-indigo-500/30 transition-colors print:border-gray-200 print:rounded-xl">
                <div className="space-y-6 print:p-0">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-[9px] font-black tracking-[0.3em] text-indigo-400 uppercase">{p.platform || p.category}</span>
                      <div className="flex items-center gap-4 no-print">
                        {p.link && (
                            <button 
                                onClick={(e) => handleCopyLink(p.link!, `featured-${p.title}`, e)}
                                className="text-slate-500 hover:text-white transition-colors"
                                title="Copy Project Link"
                            >
                                {copiedLink === `featured-${p.title}` ? <CheckCircle size={18} className="text-indigo-500" /> : <Share2 size={18} />}
                            </button>
                        )}
                        {p.link && <a href={p.link} target="_blank" className="text-slate-500 hover:text-white transition-colors"><ExternalLink size={18} /></a>}
                      </div>
                    </div>
                    <h4 className="text-3xl md:text-4xl font-bold serif-noir italic tracking-tight text-white print:text-black">{p.title}</h4>
                    <p className="text-slate-500 text-[10px] font-black tracking-[0.4em] uppercase">{p.role}</p>
                    <p className="text-base md:text-lg text-slate-400 font-light leading-relaxed serif-noir print:text-gray-700">{p.description}</p>
                  </div>
                  {p.link && (
                    <a href={p.link} target="_blank" className="pt-8 border-t border-white/5 flex items-center justify-between group/link no-print">
                      <span className="text-[9px] font-black tracking-[0.2em] text-slate-600 group-hover/link:text-indigo-400 transition-colors uppercase">Watch Project</span>
                      <ArrowUpRight size={16} className="text-slate-700 group-hover/link:text-indigo-400 transition-all" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comprehensive Experience Index */}
      <section className="py-20 md:py-32 bg-zinc-950 border-t border-white/5 print:bg-white print:py-8">
        <div className="max-w-[1400px] mx-auto px-6 md:px-10">
          <div className="mb-12 md:mb-20 flex flex-col md:flex-row md:items-center justify-between gap-8 print:mb-8">
            <h3 className="text-4xl md:text-5xl font-black serif-noir text-white tracking-tighter italic print:text-black">Full Project History</h3>
            <div className="flex flex-wrap gap-2 md:gap-3 no-print">
              {['All', 'Non-Fiction', 'Documentary', 'Commercial', 'Sports', 'Fiction'].map(cat => (
                <button
                  key={cat}
                  onClick={() => setFilter(cat)}
                  className={`px-4 md:px-6 py-2 md:py-2.5 rounded-full text-[8px] md:text-[9px] font-black tracking-[0.2em] md:tracking-[0.3em] uppercase transition-all ${
                    filter === cat ? 'bg-indigo-600 text-white' : 'bg-white/5 text-slate-500 hover:bg-white/10'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 print:gap-4">
            {(filter === 'All' ? resumeData.allProjects : resumeData.allProjects.filter(p => p.category === filter)).map((p, i) => (
              <div 
                key={i} 
                onClick={() => setSelectedProject(p)}
                className="glass-noir p-6 md:p-8 rounded-2xl md:rounded-[1.5rem] border border-white/5 flex flex-col justify-between min-h-[250px] md:h-[320px] hover:bg-white/[0.02] transition-colors group cursor-pointer print:border-gray-200 print:rounded-lg print:h-auto print:p-6 print:break-inside-avoid"
              >
                <div>
                  <div className="flex justify-between items-start mb-4 md:mb-6">
                    <div className="text-indigo-500/50 group-hover:text-indigo-500 transition-colors print:text-indigo-700">{getCategoryIcon(p.category)}</div>
                  </div>
                  <h5 className="text-lg md:text-xl font-bold text-white mb-2 serif-noir italic print:text-black">{p.title}</h5>
                  <p className="text-[9px] font-black tracking-[0.2em] text-slate-500 uppercase mb-4">{p.role}</p>
                  <p className="text-xs text-slate-400 font-light leading-relaxed line-clamp-4 print:text-gray-600 print:line-clamp-none">{p.description}</p>
                </div>
                {p.link && (
                  <div className="pt-4 border-t border-white/5 flex items-center justify-between no-print">
                    <a 
                        href={p.link} 
                        target="_blank" 
                        onClick={(e) => e.stopPropagation()}
                        className="flex items-center gap-2 group/link"
                    >
                        <span className="text-[9px] font-black tracking-[0.2em] text-slate-600 group-hover/link:text-indigo-400 transition-colors uppercase">Project Link</span>
                        <ArrowUpRight size={14} className="text-slate-800 group-hover/link:text-indigo-400 transition-all" />
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <div className="mt-12 md:mt-20 p-8 md:p-12 glass-noir rounded-3xl md:rounded-[2.5rem] border border-white/5 space-y-6 print:border-gray-200 print:rounded-lg print:p-6">
            <h4 className="text-[10px] font-black tracking-[0.4em] text-indigo-400 uppercase">Statement of Purpose</h4>
            <p className="text-slate-400 text-base md:text-lg font-light leading-relaxed serif-noir italic print:text-gray-700">
              "My interaction with management personnel at different levels has given me the opportunity to build upon my communication skills and understand the working environment in different and diverse organizations. I would welcome an opportunity to consolidate and expand my knowledge leading to a career growth and positive contribution to an organization. My academic background, ability to work in and with a team, will definitely be an additional advantage in pursuing my objectives and contributing greatly in an organization."
            </p>
          </div>
        </div>
      </section>

      {/* Footer & Academics */}
      <footer className="relative py-20 md:py-40 bg-black text-white overflow-hidden print:bg-white print:text-black print:py-8">
        <div className="relative z-10 max-w-[1400px] mx-auto px-6 md:px-10">
          <div className="grid lg:grid-cols-2 gap-12 md:gap-24 items-start print:gap-12">
            <div className="space-y-8 md:space-y-10">
              <h2 className="text-5xl md:text-6xl lg:text-8xl font-black serif-noir italic leading-none tracking-tighter print:text-black">
                Professional <br /> <span className="text-indigo-500">Integrity.</span>
              </h2>
              <p className="text-slate-500 text-sm max-w-sm italic print:text-gray-600">"I hereby affirm that all the details furnished above are true to the best of my knowledge."</p>
              <div className="flex flex-col sm:flex-row gap-4 md:gap-6 no-print">
                <a href={`mailto:${resumeData.email}`} className="flex items-center justify-center gap-3 px-8 md:px-10 py-3 md:py-4 bg-white text-black rounded-full font-black text-[9px] md:text-[10px] uppercase tracking-[0.3em] hover:bg-indigo-600 hover:text-white transition-all shadow-xl">
                  <Mail size={16} /> Contact Me
                </a>
                <div className="flex items-center justify-center px-8 md:px-10 py-3 md:py-4 glass-noir rounded-full text-[9px] md:text-[10px] font-black uppercase tracking-[0.3em] text-slate-500">
                  {resumeData.phone}
                </div>
              </div>
            </div>

            <div className="glass-noir p-8 md:p-12 rounded-3xl md:rounded-[3rem] border border-white/5 space-y-8 md:space-y-10 print:border-gray-200 print:rounded-lg print:p-6">
              <h3 className="text-[10px] font-black tracking-[0.5em] text-indigo-500 uppercase">Academic Credentials</h3>
              <div className="space-y-8 md:space-y-10">
                {resumeData.education.map((edu, i) => (
                  <div key={i} className="space-y-2 border-l-2 border-indigo-500/20 pl-6 print:border-indigo-700">
                    <h4 className="text-lg md:text-xl font-bold serif-noir text-white print:text-black">{edu.degree}</h4>
                    <p className="text-indigo-400 text-[8px] md:text-[9px] font-black tracking-[0.2em] uppercase print:text-indigo-700">{edu.institution} • {edu.year}</p>
                    <p className="text-slate-500 text-xs font-light italic print:text-gray-600">{edu.specialization}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-20 md:mt-32 pt-8 md:pt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6 md:gap-8 print:mt-12 print:pt-6 print:border-gray-300">
            <div className="flex items-center gap-4">
              <span className="serif-noir italic text-xl md:text-2xl font-bold text-white tracking-tighter uppercase print:text-black">{resumeData.name}.</span>
            </div>
            <div className="text-[9px] font-black tracking-[0.5em] text-slate-700 uppercase space-y-2 text-center md:text-right print:text-gray-500">
              <p>© {new Date().getFullYear()} Kunal Mavani Portfolio</p>
            </div>
          </div>
        </div>
      </footer>

      {/* Project Quick View Modal */}
      {selectedProject && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-10 no-print">
          <div 
            className="absolute inset-0 bg-black/90 backdrop-blur-sm transition-opacity" 
            onClick={() => setSelectedProject(null)}
          />
          <div className="relative w-full max-w-3xl bg-[#080808] border border-white/10 rounded-3xl md:rounded-[2rem] shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-200">
            <div className="absolute top-0 right-0 p-4 md:p-6 z-10">
              <button 
                onClick={() => setSelectedProject(null)}
                className="p-2 rounded-full bg-black/50 text-white/50 hover:bg-white hover:text-black hover:scale-110 transition-all backdrop-blur-md border border-white/5"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-8 md:p-12 overflow-y-auto custom-scrollbar">
              <div className="space-y-8">
                <div>
                  <div className="flex items-center gap-3 text-indigo-500 mb-6">
                    {getCategoryIcon(selectedProject.category)}
                    <span className="text-[10px] font-black tracking-[0.3em] uppercase">{selectedProject.category}</span>
                    {selectedProject.platform && (
                        <>
                            <span className="w-1 h-1 bg-slate-700 rounded-full" />
                            <span className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase">{selectedProject.platform}</span>
                        </>
                    )}
                  </div>
                  <h3 className="text-4xl md:text-5xl font-black serif-noir italic text-white leading-none tracking-tight mb-4">
                    {selectedProject.title}
                  </h3>
                  <div className="flex flex-wrap items-center gap-4">
                    <span className="px-4 py-1.5 bg-white/5 rounded-full text-[10px] font-black tracking-[0.2em] text-indigo-400 uppercase border border-white/5">
                        {selectedProject.role}
                    </span>
                  </div>
                </div>

                <div className="w-full h-px bg-gradient-to-r from-indigo-500/50 to-transparent" />

                <div className="space-y-4">
                  <h4 className="text-[10px] font-black tracking-[0.2em] text-slate-500 uppercase flex items-center gap-2">
                    <FileText size={14} /> Project Description
                  </h4>
                  <p className="text-lg md:text-xl text-slate-300 font-light leading-relaxed serif-noir">
                    {selectedProject.description}
                  </p>
                </div>

                {selectedProject.link && (
                  <div className="pt-8 flex justify-start">
                    <a 
                      href={selectedProject.link} 
                      target="_blank" 
                      className="group flex items-center gap-4 px-8 py-4 bg-white text-black rounded-full text-[10px] font-black tracking-[0.2em] uppercase hover:bg-indigo-600 hover:text-white transition-all w-full md:w-auto justify-center md:justify-start"
                    >
                      <span>View Project</span>
                      <ArrowUpRight size={16} className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
