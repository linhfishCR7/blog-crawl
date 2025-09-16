import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const CrawledContentPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Crawled Content - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Crawled Content Review
        </Typography>
        <Typography>Crawled content review interface will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default CrawledContentPage;
