import React from 'react';

// Прими пропс од App.js
const List = ({ data }) => {
    return (
        <div>
            <h1>List Page</h1>
            <ul>

                {data.map((item) => (
                    <li key={item.id}>{item.name}</li>
                    ))}
            </ul>
        </div>
    );
};

export default List;
