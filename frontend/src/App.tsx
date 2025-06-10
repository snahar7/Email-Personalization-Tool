import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { ChakraProvider, Box, Flex, VStack, HStack, Text, Button, useColorModeValue } from '@chakra-ui/react';
import { FiUsers, FiMail, FiBarChart2, FiSettings } from 'react-icons/fi';

// Import components
import ProspectsList from './components/ProspectsList';
import EmailTemplates from './components/EmailTemplates';
import Analytics from './components/Analytics';

const NavItem = ({ icon, children, to }: { icon: React.ReactElement; children: React.ReactNode; to: string }) => {
  return (
    <Link to={to} style={{ textDecoration: 'none' }}>
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        _hover={{
          bg: 'cyan.400',
          color: 'white',
        }}
      >
        {icon}
        <Text ml="4" fontWeight="semibold">
          {children}
        </Text>
      </Flex>
    </Link>
  );
};

function App() {
  return (
    <ChakraProvider>
      <Router>
        <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
          <Flex h="100vh">
            {/* Sidebar */}
            <Box
              w="64"
              bg={useColorModeValue('white', 'gray.800')}
              borderRight="1px"
              borderRightColor={useColorModeValue('gray.200', 'gray.700')}
              py="5"
            >
              <VStack spacing="4" align="stretch">
                <Box px="4" py="2">
                  <Text fontSize="2xl" fontWeight="bold" color="cyan.500">
                    Email Tool
                  </Text>
                </Box>
                <NavItem icon={<FiUsers />} to="/">
                  Prospects
                </NavItem>
                <NavItem icon={<FiMail />} to="/templates">
                  Email Templates
                </NavItem>
                <NavItem icon={<FiBarChart2 />} to="/analytics">
                  Analytics
                </NavItem>
                <NavItem icon={<FiSettings />} to="/settings">
                  Settings
                </NavItem>
              </VStack>
            </Box>

            {/* Main Content */}
            <Box flex="1" p="8" overflowY="auto">
              <Routes>
                <Route path="/" element={<ProspectsList />} />
                <Route path="/templates" element={<EmailTemplates />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </Box>
          </Flex>
        </Box>
      </Router>
    </ChakraProvider>
  );
}

export default App;
