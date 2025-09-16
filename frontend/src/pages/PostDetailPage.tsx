import React from 'react';
import { Container, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

const PostDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  return (
    <>
      <Helmet>
        <title>Post Detail - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Post Detail: {slug}
        </Typography>
        <Typography>Post detail view will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default PostDetailPage;
