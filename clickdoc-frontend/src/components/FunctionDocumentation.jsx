import { Link } from "react-router-dom";
import { FileText, Upload, CheckCircle, RefreshCw, Edit } from "lucide-react";

const FunctionDocumentation = () => {
  const uploadedFiles = ["Main.java", "UserLogin.java", "UserRegister.java"];
  const filename = "test_diagram.py";

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* Header (same as Dashboard) */}
      <header className="bg-white px-6 py-4 border-b border-gray-200 shadow-sm w-full">
        <div className="flex items-center w-full">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white text-lg font-bold">
              📄
            </div>
            <span className="text-2xl font-semibold text-gray-900">ClickDoc</span>
          </div>
        </div>
      </header>

      <div className="flex min-h-[calc(100vh-80px)]">
        {/* Sidebar (styled like Dashboard but slightly larger text/icons) */}
        <aside className="w-72 bg-white border-r border-gray-200 p-6">
          {/* Uploaded Files */}
          <div className="mb-8">
            <div className="flex items-center gap-2 text-base font-semibold mb-4 text-gray-700">
              <div className="w-5 h-5 bg-orange-500 rounded flex items-center justify-center text-white text-xs">
                ↑
              </div>
              File Uploaded
            </div>
            <ul className="space-y-3">
              {uploadedFiles.map((file, i) => (
                <li
                  key={i}
                  className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-50 cursor-pointer text-gray-800 text-sm"
                >
                  <FileText className="w-5 h-5 text-purple-600" />
                  <span className="text-base">{file}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Generated Files */}
          <div>
            <div className="flex items-center gap-2 text-base font-semibold mb-4 text-gray-700">
              <div className="w-5 h-5 bg-green-500 rounded flex items-center justify-center text-white text-xs">
                ✓
              </div>
              File Generated
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 px-10 py-8 bg-gray-50">
          <div className="max-w-5xl">
            <h2 className="text-3xl font-semibold mb-2">Function Documentation</h2>
            <p className="text-gray-600 mb-8">
              Auto-generated function references and analysis
            </p>

            {/* Documentation Card (styled like dashboard cards) */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200">
              {/* Gradient Header */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4 rounded-t-xl">
                <h3 className="text-white font-semibold text-lg">
                  Generated Documentation
                </h3>
              </div>

              {/* Doc Content */}
              <div className="p-6">
                <h4 className="text-blue-600 font-medium text-lg mb-4">
                  {filename}
                </h4>
                <pre className="bg-gray-100 p-4 rounded-lg whitespace-pre-wrap leading-relaxed font-mono text-sm border border-gray-200">
{`def add_numbers(a, b):
    """Adds two numbers and returns the result."""
    return a + b

def multiply(x, y):
    """Multiplies two numbers and returns the result."""
    return x * y
`}
                </pre>
              </div>

              {/* Action Buttons */}
              <div className="px-6 pb-6">
                <div className="flex gap-3">
                  <button className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-md font-medium hover:bg-blue-700 transition-colors">
                    <RefreshCw className="w-4 h-4" />
                    Regenerate
                  </button>
                  <button className="flex items-center gap-2 bg-gray-200 text-gray-800 px-5 py-2.5 rounded-md font-medium hover:bg-gray-300 transition-colors">
                    <Edit className="w-4 h-4" />
                    Edit
                  </button>
                  <Link to="/dashboard">
                    <button className="ml-2 bg-gray-100 text-gray-700 px-4 py-2.5 rounded-md text-sm font-medium hover:bg-gray-200 transition-colors">
                      ← Back
                    </button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default FunctionDocumentation;
