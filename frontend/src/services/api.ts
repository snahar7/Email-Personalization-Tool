import axios from 'axios';
import { Company, Prospect } from '../types';

const baseURL = 'http://localhost:8000/api';

export const api = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized access
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// API endpoints
export const endpoints = {
    // Prospects
    getProspects: () => api.get('/prospects/'),
    getProspect: (id: number) => api.get(`/prospects/${id}`),
    createProspect: (data: any) => api.post('/prospects/', data),
    updateProspect: (id: number, data: any) => api.put(`/prospects/${id}`, data),
    deleteProspect: (id: number) => api.delete(`/prospects/${id}`),

    // Companies
    getCompanies: () => api.get('/companies/'),
    getCompany: (id: number) => api.get(`/companies/${id}`),
    createCompany: (data: any) => api.post('/companies/', data),
    updateCompany: (id: number, data: any) => api.put(`/companies/${id}`, data),
    deleteCompany: (id: number) => api.delete(`/companies/${id}`),

    // Email Templates
    getTemplates: () => api.get('/templates/'),
    getTemplate: (id: number) => api.get(`/templates/${id}`),
    createTemplate: (data: any) => api.post('/templates/', data),
    updateTemplate: (id: number, data: any) => api.put(`/templates/${id}`, data),
    deleteTemplate: (id: number) => api.delete(`/templates/${id}`),
    createTemplateVariant: (id: number) => api.post(`/templates/${id}/variants`),

    // Email Engagement
    getEngagementMetrics: (days: number) => api.get(`/engagements/metrics/?days=${days}`),
    getProspectEngagement: (id: number) => api.get(`/prospects/${id}/engagement/`),
    createEngagement: (data: any) => api.post('/engagements/', data),
    updateEngagement: (id: number, data: any) => api.put(`/engagements/${id}`, data),
};

export const getProspects = async (): Promise<Prospect[]> => {
    const response = await api.get('/prospects/');
    return response.data;
};

export const getProspect = async (id: number): Promise<Prospect> => {
    const response = await api.get(`/prospects/${id}`);
    return response.data;
};

export const createProspect = async (prospect: Omit<Prospect, 'id' | 'created_at' | 'updated_at'>): Promise<Prospect> => {
    const response = await api.post('/prospects/', prospect);
    return response.data;
};

export const getCompanies = async (): Promise<Company[]> => {
    const response = await api.get('/companies/');
    return response.data;
};

export const getCompany = async (id: number): Promise<Company> => {
    const response = await api.get(`/companies/${id}`);
    return response.data;
};

export const createCompany = async (company: Omit<Company, 'id' | 'created_at' | 'updated_at'>): Promise<Company> => {
    const response = await api.post('/companies/', company);
    return response.data;
};

export const updateCompany = async (id: number, company: Partial<Company>): Promise<Company> => {
    const response = await api.put(`/companies/${id}`, company);
    return response.data;
}; 