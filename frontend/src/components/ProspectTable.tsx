import React, { useEffect, useState } from 'react';
import {
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Box,
    Spinner,
    Text,
    IconButton,
    Link,
    useToast,
} from '@chakra-ui/react';
import { FiEdit2, FiTrash2 } from 'react-icons/fi';
import { Prospect } from '../types';
import { getProspects } from '../services/api';

const ProspectTable: React.FC = () => {
    const [prospects, setProspects] = useState<Prospect[]>([]);
    const [loading, setLoading] = useState(true);
    const toast = useToast();

    useEffect(() => {
        const fetchProspects = async () => {
            try {
                const data = await getProspects();
                setProspects(data);
            } catch (err) {
                toast({
                    title: 'Error fetching prospects',
                    description: 'Failed to load prospects data',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
                console.error('Error fetching prospects:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchProspects();
    }, [toast]);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <Spinner size="xl" />
            </Box>
        );
    }

    return (
        <Box overflowX="auto">
            <Table variant="simple">
                <Thead>
                    <Tr>
                        <Th>Name</Th>
                        <Th>Email</Th>
                        <Th>Position</Th>
                        <Th>Company</Th>
                        <Th>LinkedIn</Th>
                        <Th>Actions</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {prospects.map((prospect) => (
                        <Tr key={prospect.id}>
                            <Td>{prospect.name}</Td>
                            <Td>{prospect.email}</Td>
                            <Td>{prospect.position}</Td>
                            <Td>{prospect.company?.name || '-'}</Td>
                            <Td>
                                {prospect.linkedin_url ? (
                                    <Link
                                        href={prospect.linkedin_url}
                                        isExternal
                                        color="blue.500"
                                    >
                                        View Profile
                                    </Link>
                                ) : (
                                    '-'
                                )}
                            </Td>
                            <Td>
                                <IconButton
                                    aria-label="Edit prospect"
                                    icon={<FiEdit2 />}
                                    size="sm"
                                    colorScheme="blue"
                                    mr={2}
                                />
                                <IconButton
                                    aria-label="Delete prospect"
                                    icon={<FiTrash2 />}
                                    size="sm"
                                    colorScheme="red"
                                />
                            </Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </Box>
    );
};

export default ProspectTable; 