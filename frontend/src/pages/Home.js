import React from 'react';
import { FileText, Upload, Search, GitBranch, Settings, Shield, Zap, BarChart3, Workflow } from 'lucide-react';

function Home() {
  const handleUploadClick = () => {
    // In your actual app, this will be: navigate('/upload');
    window.location.href = '/upload';
  };

  const features = [
    {
      title: "Auto-Generate",
      description: "Generate documentation from your code automatically with AI assistance",
      icon: <Zap className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Function Documentation", 
      description: "Extract and explain individual functions with ability to add custom comments",
      icon: <FileText className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Module Relationship",
      description: "Understand and document how different code modules connect and interact",
      icon: <GitBranch className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Tech Stack Documentation",
      description: "Automatically identify and document tools, languages, and dependencies used",
      icon: <Settings className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Setup & Installation Guide",
      description: "Generate comprehensive guidelines on how to install and run your code",
      icon: <Shield className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Form Validation Analysis",
      description: "Extract and explain validation rules from form code automatically",
      icon: <Shield className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Relationship Diagrams",
      description: "Visual maps showing how components and modules connect in your system",
      icon: <BarChart3 className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Smart Search",
      description: "Ask questions about your uploaded code and get instant AI-powered answers",
      icon: <Search className="w-8 h-8 text-blue-600 mb-3" />
    },
    {
      title: "Flow Diagrams",
      description: "Generate process flow and execution path visualizations from your code",
      icon: <Workflow className="w-8 h-8 text-blue-600 mb-3" />
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6 bg-white shadow-sm">
        <div className="text-2xl font-bold text-blue-600">
          ClickDoc
        </div>
        <button 
          onClick={handleUploadClick}
          className="bg-white text-blue-600 px-6 py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center gap-2"
        >
          <Upload className="w-5 h-5" />
          Upload
        </button>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-500 to-blue-700 text-white text-center py-16 px-8">
        <h1 className="text-5xl font-bold mb-6">
          ClickDoc
        </h1>
        <h2 className="text-2xl mb-8 max-w-3xl mx-auto opacity-90">
          Documentation in One Click — Smarter, Faster, Ready to Use
        </h2>
        <button 
          onClick={handleUploadClick}
          className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg hover:bg-gray-100 transition-colors font-semibold"
        >
          Get Started
        </button>
      </section>

      {/* Features Grid */}
      <section className="px-8 py-12">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-white p-6 rounded-lg hover:shadow-lg transition-all duration-300 border border-gray-100">
              <div className="flex flex-col items-start">
                {feature.icon}
                <h3 className="text-xl font-semibold text-gray-800 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="text-center py-16 px-8 bg-gray-50">
        <button 
          onClick={handleUploadClick}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg hover:bg-blue-700 transition-colors"
        >
          Get Started -- It's free
        </button>
      </section>
    </div>
  );
}

export default Home;