import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import loginImg from '../assets/login.png';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    navigate('/dashboard', { state: { name: username } });
  };

  return (
    <div className="container">
      <div className="form-box">
        <div className="image-container">
          <img src={loginImg} alt="login" />
        </div>
        <div className="form-container">
          <h2>Login</h2>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={handleLogin}>Login</button>
          <div className="link">
            <Link to="/signup">New User? Signup</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
