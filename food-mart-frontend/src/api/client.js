import axios from 'axios';

const apiClient = axios.create({ baseURL: 'http://localhost/api', withCredentials: true });

apiClient.interceptors.request.use((config) => {
	const accessToken = localStorage.getItem('foodMartAccessToken');
	if (accessToken) {
		config.headers.Authorization = `Bearer ${accessToken}`;
	}
	return config;
});

export default apiClient;
