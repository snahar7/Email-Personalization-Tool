import React, { useEffect, useState } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    IconButton,
    Typography,
    Box,
    CircularProgress,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Prospect } from '../types';
import { getProspects } from '../services/api';

const ProspectTable: React.FC = () => {
    const [prospects, setProspects] = useState<Prospect[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProspects = async () => {
            try {
                const data = await getProspects();
                setProspects(data);
                setError(null);
            } catch (err) {
                setError('Failed to fetch prospects');
                console.error('Error fetching prospects:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchProspects();
    }, []);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }

    if (error) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <Typography color="error">{error}</Typography>
            </Box>
        );
    }

    return (
        <TableContainer component={Paper}>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Email</TableCell>
                        <TableCell>Position</TableCell>
                        <TableCell>Company</TableCell>
                        <TableCell>LinkedIn</TableCell>
                        <TableCell>Actions</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {prospects.map((prospect) => (
                        <TableRow key={prospect.id}>
                            <TableCell>{prospect.name}</TableCell>
                            <TableCell>{prospect.email}</TableCell>
                            <TableCell>{prospect.position}</TableCell>
                            <TableCell>{prospect.company?.name || '-'}</TableCell>
                            <TableCell>
                                {prospect.linkedin_url ? (
                                    <a
                                        href={prospect.linkedin_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        View Profile
                                    </a>
                                ) : (
                                    '-'
                                )}
                            </TableCell>
                            <TableCell>
                                <IconButton size="small" color="primary">
                                    <EditIcon />
                                </IconButton>
                                <IconButton size="small" color="error">
                                    <DeleteIcon />
                                </IconButton>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
};

export default ProspectTable; 