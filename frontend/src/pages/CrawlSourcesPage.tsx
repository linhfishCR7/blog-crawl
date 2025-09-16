import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const CrawlSourcesPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Crawl Sources - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Crawl Sources Management
        </Typography>
        <Typography>Crawl sources management interface will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default CrawlSourcesPage;
