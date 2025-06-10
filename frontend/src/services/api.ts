import axios from 'axios';
import { Company, Prospect } from '../types';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

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