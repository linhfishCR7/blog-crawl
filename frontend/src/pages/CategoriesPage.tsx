import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const CategoriesPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Categories - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Categories Management
        </Typography>
        <Typography>Categories management interface will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default CategoriesPage;
