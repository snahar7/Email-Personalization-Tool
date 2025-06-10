import React from 'react';
import { Container, Typography, Box, AppBar, Toolbar } from '@mui/material';
import ProspectTable from './components/ProspectTable';

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Email Personalization Tool
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Prospects Dashboard
        </Typography>
        <ProspectTable />
      </Container>
    </Box>
  );
}

export default App;
