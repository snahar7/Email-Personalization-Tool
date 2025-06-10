import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Grid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Badge,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Textarea,
  Input,
  Select,
} from '@chakra-ui/react';
import { FiPlus, FiEdit2, FiTrash2, FiCopy } from 'react-icons/fi';
import { api } from '../services/api';

interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  company_id: number;
  is_active: boolean;
  variant: string | null;
  performance_metrics: {
    opens: number;
    clicks: number;
    replies: number;
  } | null;
}

const EmailTemplates = () => {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<EmailTemplate | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/templates/');
      setTemplates(response.data);
    } catch (error) {
      toast({
        title: 'Error fetching templates',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleCreateTemplate = () => {
    setSelectedTemplate(null);
    onOpen();
  };

  const handleEditTemplate = (template: EmailTemplate) => {
    setSelectedTemplate(template);
    onOpen();
  };

  const handleSaveTemplate = async (templateData: Partial<EmailTemplate>) => {
    try {
      if (selectedTemplate) {
        await api.put(`/templates/${selectedTemplate.id}`, templateData);
      } else {
        await api.post('/templates/', templateData);
      }
      fetchTemplates();
      onClose();
      toast({
        title: 'Template saved successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error saving template',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleCreateVariant = async (template: EmailTemplate) => {
    try {
      await api.post(`/templates/${template.id}/variants`);
      fetchTemplates();
      toast({
        title: 'Template variant created',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error creating variant',
        status: 'error',
        duration: 3000,
      });
    }
  };

  return (
    <VStack spacing={4} align="stretch">
      <HStack justify="space-between">
        <Text fontSize="2xl" fontWeight="bold">
          Email Templates
        </Text>
        <Button leftIcon={<FiPlus />} colorScheme="cyan" onClick={handleCreateTemplate}>
          New Template
        </Button>
      </HStack>

      <Grid templateColumns="repeat(auto-fill, minmax(300px, 1fr))" gap={4}>
        {templates.map((template) => (
          <Card key={template.id}>
            <CardHeader>
              <HStack justify="space-between">
                <Text fontWeight="bold">{template.name}</Text>
                <Badge colorScheme={template.is_active ? 'green' : 'gray'}>
                  {template.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </HStack>
            </CardHeader>
            <CardBody>
              <Text fontWeight="semibold" mb={2}>
                Subject: {template.subject}
              </Text>
              <Text noOfLines={3}>{template.body}</Text>
              {template.performance_metrics && (
                <HStack mt={4} spacing={4}>
                  <Text>Opens: {template.performance_metrics.opens}</Text>
                  <Text>Clicks: {template.performance_metrics.clicks}</Text>
                  <Text>Replies: {template.performance_metrics.replies}</Text>
                </HStack>
              )}
            </CardBody>
            <CardFooter>
              <HStack spacing={2}>
                <Button
                  size="sm"
                  leftIcon={<FiEdit2 />}
                  onClick={() => handleEditTemplate(template)}
                >
                  Edit
                </Button>
                <Button
                  size="sm"
                  leftIcon={<FiCopy />}
                  onClick={() => handleCreateVariant(template)}
                >
                  Create Variant
                </Button>
              </HStack>
            </CardFooter>
          </Card>
        ))}
      </Grid>

      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {selectedTemplate ? 'Edit Template' : 'New Template'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <Input
                placeholder="Template Name"
                defaultValue={selectedTemplate?.name}
              />
              <Input
                placeholder="Subject"
                defaultValue={selectedTemplate?.subject}
              />
              <Textarea
                placeholder="Email Body"
                defaultValue={selectedTemplate?.body}
                minH="200px"
              />
              <Select placeholder="Select Company">
                {/* Add company options */}
              </Select>
              <Button
                colorScheme="blue"
                onClick={() => handleSaveTemplate({})}
                width="full"
              >
                Save Template
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default EmailTemplates; 