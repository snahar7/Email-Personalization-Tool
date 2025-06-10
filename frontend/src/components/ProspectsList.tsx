import React, { useState, useEffect } from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Input,
  HStack,
  VStack,
  Text,
  useToast,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
} from '@chakra-ui/react';
import { FiMoreVertical, FiMail, FiUserPlus } from 'react-icons/fi';
import { api } from '../services/api';

interface Prospect {
  id: number;
  name: string;
  email: string;
  position: string;
  company: {
    name: string;
    industry: string;
  };
  status: string;
  engagement_score: number;
}

const ProspectsList = () => {
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const toast = useToast();

  useEffect(() => {
    fetchProspects();
  }, []);

  const fetchProspects = async () => {
    try {
      const response = await api.get('/prospects/');
      setProspects(response.data);
    } catch (error) {
      toast({
        title: 'Error fetching prospects',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      new: 'gray',
      contacted: 'blue',
      engaged: 'green',
      qualified: 'purple',
      converted: 'teal',
    };
    return colors[status as keyof typeof colors] || 'gray';
  };

  const filteredProspects = prospects.filter(
    (prospect) =>
      prospect.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prospect.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prospect.company.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <VStack spacing={4} align="stretch">
      <HStack justify="space-between">
        <Text fontSize="2xl" fontWeight="bold">
          Prospects
        </Text>
        <Button leftIcon={<FiUserPlus />} colorScheme="cyan">
          Add Prospect
        </Button>
      </HStack>

      <Input
        placeholder="Search prospects..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        size="md"
      />

      <Box overflowX="auto">
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Email</Th>
              <Th>Position</Th>
              <Th>Company</Th>
              <Th>Status</Th>
              <Th>Engagement</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {filteredProspects.map((prospect) => (
              <Tr key={prospect.id}>
                <Td>{prospect.name}</Td>
                <Td>{prospect.email}</Td>
                <Td>{prospect.position}</Td>
                <Td>{prospect.company.name}</Td>
                <Td>
                  <Badge colorScheme={getStatusColor(prospect.status)}>
                    {prospect.status}
                  </Badge>
                </Td>
                <Td>{prospect.engagement_score}</Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Send email"
                      icon={<FiMail />}
                      size="sm"
                      colorScheme="blue"
                    />
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FiMoreVertical />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem>View Details</MenuItem>
                        <MenuItem>Edit Prospect</MenuItem>
                        <MenuItem>View Engagement History</MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>
    </VStack>
  );
};

export default ProspectsList; 