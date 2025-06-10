export interface Company {
    id: number;
    name: string;
    industry?: string;
    website?: string;
    description?: string;
    company_bio?: string;
    product_info?: string;
    key_insights?: string;
    market_position?: string;
    funding_info?: string;
    created_at: string;
    updated_at?: string;
}

export interface Prospect {
    id: number;
    name: string;
    email: string;
    position?: string;
    company_id?: number;
    linkedin_url?: string;
    created_at: string;
    updated_at?: string;
    company?: Company;
} 