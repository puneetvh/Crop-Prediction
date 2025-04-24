import React, { useState } from "react";
import "../styles.css";

const SearchBar = ({ onSearch }) => {
  const [searchInput, setSearchInput] = useState("");

  const handleInputChange = (e) => setSearchInput(e.target.value);

  const handleSearch = () => {
    if (searchInput.trim()) {
      onSearch(searchInput.trim());
      setSearchInput("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search city..."
        value={searchInput}
        onChange={handleInputChange}
        onKeyDown={handleKeyPress}
        className="search-input"
      />
      <button onClick={handleSearch} className="search-btn">🔍</button>
    </div>
  );
};

export default SearchBar;
