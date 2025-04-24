import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import loginImg from '../assets/login.png';

const Signup = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignup = async () => {
    try {
      const res = await api.post('/signup', {
        username: name,
        email,
        password,
      });

      if (res.data.message === 'Signup successful') {
        alert('Signup successful!');
        navigate('/');
      } else {
        alert(res.data.message || 'Signup failed');
      }
    } catch (err) {
      console.error('Signup error:', err);
      alert('Signup failed');
    }
  };

  return (
    <div className="container">
      <div className="form-box">
        <div className="image-container">
          <img src={loginImg} alt="signup" />
        </div>
        <div className="form-container">
          <h2>Signup</h2>
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
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
          <button onClick={handleSignup}>Signup</button>
          <div className="link">
            <Link to="/">Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
