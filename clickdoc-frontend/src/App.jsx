import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import FunctionDocumentation from './components/FunctionDocumentation';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/function_documentation" element={<FunctionDocumentation />} />
        <Route path="/" element={<Navigate to="/dashboard" />} /> {/* Default route */}
        {/* Add other routes later */}
      </Routes>
    </Router>
  );
}

export default App;