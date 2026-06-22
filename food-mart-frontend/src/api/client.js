import axios from 'axios';

const apiClient = axios.create({ 
  baseURL: 'https://mini-mart-aw0d.onrender.com/api/v1', // Make sure this matches your Flask route prefix!
  withCredentials: true 
});

export default apiClient;
