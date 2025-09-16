import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const CrawlJobsPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Crawl Jobs - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Crawl Jobs Monitoring
        </Typography>
        <Typography>Crawl jobs monitoring interface will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default CrawlJobsPage;
