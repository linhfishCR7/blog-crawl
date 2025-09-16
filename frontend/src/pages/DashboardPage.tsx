import React from 'react';
import { Container, Typography, Grid, Paper, Box } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const DashboardPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Dashboard - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Total Posts</Typography>
              <Typography variant="h4">0</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6} lg={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Crawl Sources</Typography>
              <Typography variant="h4">0</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6} lg={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Active Jobs</Typography>
              <Typography variant="h4">0</Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6} lg={3}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">Pending Content</Typography>
              <Typography variant="h4">0</Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </>
  );
};

export default DashboardPage;
