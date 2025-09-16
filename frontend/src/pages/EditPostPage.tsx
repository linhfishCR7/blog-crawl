import React from 'react';
import { Container, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

const EditPostPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  return (
    <>
      <Helmet>
        <title>Edit Post - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          Edit Post: {slug}
        </Typography>
        <Typography>Post editing form will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default EditPostPage;
