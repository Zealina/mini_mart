import axios from 'axios';

const apiClient = axios.create({ baseURL: 'http://127.0.0.1/api', withCredentials: true });

apiClient.interceptors.request.use((config) => {
	const accessToken = localStorage.getItem('foodMartAccessToken');
	if (accessToken) {
		config.headers.Authorization = `Bearer ${accessToken}`;
	}
	return config;
});

export default apiClient;
