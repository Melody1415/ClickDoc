import { Link } from 'react-router-dom';

const Dashboard = () => {
  // Mock file list (replace with API call to /api/session later)
  const uploadedFiles = ['Main.java', 'UserLogin.java', 'UserRegister.java'];

  return (
    <div className="min-h-screen bg-gray-50 w-full max-w-none m-0 p-0" style={{width: '100vw', maxWidth: 'none', margin: 0, padding: 0}}>
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
        <aside className="w-70 bg-white border-r border-gray-200 p-6">
          <div>
            <div className="flex items-center gap-2 text-sm font-medium mb-4 text-gray-600">
              <div className="w-4 h-4 bg-green-500 rounded flex items-center justify-center text-white text-xs">
                ↑
              </div>
              File Uploaded
            </div>
            <ul className="space-y-2">
              {uploadedFiles.map((file, index) => (
                <li key={index} className="flex items-center gap-2 py-2 text-gray-800 text-sm">
                  <div className="w-5 h-5 bg-gray-500 rounded flex items-center justify-center text-white text-xs">
                    📄
                  </div>
                  <span>{file}</span>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        <main className="flex-1 px-10 py-8 bg-gray-50">
          <div className="mb-10">
            <h1 className="text-3xl font-semibold text-gray-900 mb-2">Generate Documentation</h1>
            <p className="text-gray-600">Select the type of documentation to be generated</p>
          </div>

          <div className="flex flex-col items-center gap-6">
            <div className="flex gap-6 justify-center">
              <div className="w-50 h-50 bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:-translate-y-1 hover:shadow-md transition-all duration-200 cursor-pointer">
                <div className="flex flex-col items-center justify-between h-full">
                  <div className="flex flex-col items-center flex-1">
                    <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center text-xl mb-4">
                      📋
                    </div>
                    <h3 className="text-gray-900 font-medium text-sm text-center mb-4">Function Reference</h3>
                  </div>
                  <Link to="/function_documentation" className="w-full">
                    <button className="w-full bg-blue-600 text-white rounded-md py-2.5 px-5 text-sm font-medium hover:bg-blue-700 transition-colors">
                      Generate
                    </button>
                  </Link>
                </div>
              </div>

              <div className="w-50 h-50 bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:-translate-y-1 hover:shadow-md transition-all duration-200 cursor-pointer">
                <div className="flex flex-col items-center justify-between h-full">
                  <div className="flex flex-col items-center flex-1">
                    <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-lg flex items-center justify-center text-xl mb-4">
                      ⚙️
                    </div>
                    <h3 className="text-gray-900 font-medium text-sm text-center mb-4">Module Relationships</h3>
                  </div>
                  <button className="w-full bg-blue-600 text-white rounded-md py-2.5 px-5 text-sm font-medium hover:bg-blue-700 transition-colors">
                    Generate
                  </button>
                </div>
              </div>

              <div className="w-50 h-50 bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:-translate-y-1 hover:shadow-md transition-all duration-200 cursor-pointer">
                <div className="flex flex-col items-center justify-between h-full">
                  <div className="flex flex-col items-center flex-1">
                    <div className="w-12 h-12 bg-green-50 text-green-600 rounded-lg flex items-center justify-center text-xl mb-4">
                      🛡️
                    </div>
                    <h3 className="text-gray-900 font-medium text-sm text-center mb-4">Validation Rules</h3>
                  </div>
                  <button className="w-full bg-blue-600 text-white rounded-md py-2.5 px-5 text-sm font-medium hover:bg-blue-700 transition-colors">
                    Generate
                  </button>
                </div>
              </div>
            </div>

            <div className="flex gap-6 justify-center">
              <div className="w-50 h-50 bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:-translate-y-1 hover:shadow-md transition-all duration-200 cursor-pointer">
                <div className="flex flex-col items-center justify-between h-full">
                  <div className="flex flex-col items-center flex-1">
                    <div className="w-12 h-12 bg-orange-50 text-orange-600 rounded-lg flex items-center justify-center text-xl mb-4">
                      🖥️
                    </div>
                    <h3 className="text-gray-900 font-medium text-sm text-center mb-4">Setup Guide</h3>
                  </div>
                  <button className="w-full bg-blue-600 text-white rounded-md py-2.5 px-5 text-sm font-medium hover:bg-blue-700 transition-colors">
                    Generate
                  </button>
                </div>
              </div>

              <div className="w-50 h-50 bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:-translate-y-1 hover:shadow-md transition-all duration-200 cursor-pointer">
                <div className="flex flex-col items-center justify-between h-full">
                  <div className="flex flex-col items-center flex-1">
                    <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center text-xl mb-4">
                      📦
                    </div>
                    <h3 className="text-gray-900 font-medium text-sm text-center mb-4">Tech Stack</h3>
                  </div>
                  <button className="w-full bg-blue-600 text-white rounded-md py-2.5 px-5 text-sm font-medium hover:bg-blue-700 transition-colors">
                    Generate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;