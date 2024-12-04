import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    return (
        <div>
            <h1>Welcome to Home Page</h1>
            <Link to="/list">Go to List</Link>
        </div>
    );
};

export default Home;
