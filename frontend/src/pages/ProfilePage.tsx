import React from 'react';
import { Container, Typography } from '@mui/material';
import { Helmet } from 'react-helmet-async';

const ProfilePage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Profile - Blog CMS</title>
      </Helmet>
      
      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          User Profile
        </Typography>
        <Typography>User profile management interface will be implemented here.</Typography>
      </Container>
    </>
  );
};

export default ProfilePage;
