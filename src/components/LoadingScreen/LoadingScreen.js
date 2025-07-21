import React from 'react';
import { Box, Typography, CircularProgress, LinearProgress } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';

// Animations
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
`;

// Styled components
const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
  padding: theme.spacing(3),
}));

const LogoContainer = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(4),
  animation: `${fadeIn} 0.8s ease-out`,
}));

const LoadingContent = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  maxWidth: 400,
  animation: `${fadeIn} 1s ease-out 0.3s both`,
}));

const StatusText = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(2),
  color: theme.palette.text.secondary,
  animation: `${pulse} 2s ease-in-out infinite`,
}));

const ProgressContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  marginTop: theme.spacing(3),
}));

// AWS Logo SVG Component
const AWSLogo = () => (
  <svg width="80" height="48" viewBox="0 0 80 48" fill="none">
    <rect width="80" height="48" rx="8" fill="#232F3E"/>
    <path d="M20 32C20 33.1 19.1 34 18 34H14C12.9 34 12 33.1 12 32V16C12 14.9 12.9 14 14 14H18C19.1 14 20 14.9 20 16V32Z" fill="#FF9900"/>
    <path d="M32 32C32 33.1 31.1 34 30 34H26C24.9 34 24 33.1 24 32V20C24 18.9 24.9 18 26 18H30C31.1 18 32 18.9 32 20V32Z" fill="#FF9900"/>
    <path d="M44 32C44 33.1 43.1 34 42 34H38C36.9 34 36 33.1 36 32V24C36 22.9 36.9 22 38 22H42C43.1 22 44 22.9 44 24V32Z" fill="#FF9900"/>
    <path d="M56 32C56 33.1 55.1 34 54 34H50C48.9 34 48 33.1 48 32V18C48 16.9 48.9 16 50 16H54C55.1 16 56 16.9 56 18V32Z" fill="#FF9900"/>
    <path d="M68 32C68 33.1 67.1 34 66 34H62C60.9 34 60 33.1 60 32V26C60 24.9 60.9 24 62 24H66C67.1 24 68 24.9 68 26V32Z" fill="#FF9900"/>
  </svg>
);

const LoadingScreen = () => {
  const [progress, setProgress] = React.useState(0);
  const [statusMessage, setStatusMessage] = React.useState('Inicializando sistema...');

  React.useEffect(() => {
    const messages = [
      'Inicializando sistema...',
      'Conectando con servicios AWS...',
      'Verificando MCPs en ECS...',
      'Configurando Lambda Arquitecto...',
      'Preparando interfaz...',
      'Sistema listo!'
    ];

    let currentMessage = 0;
    const timer = setInterval(() => {
      setProgress((prevProgress) => {
        const newProgress = prevProgress + 20;
        
        if (currentMessage < messages.length - 1) {
          setStatusMessage(messages[currentMessage]);
          currentMessage++;
        }
        
        if (newProgress >= 100) {
          clearInterval(timer);
          setStatusMessage('Sistema listo!');
          return 100;
        }
        
        return newProgress;
      });
    }, 300);

    return () => {
      clearInterval(timer);
    };
  }, []);

  return (
    <LoadingContainer>
      <LogoContainer>
        <AWSLogo />
      </LogoContainer>
      
      <LoadingContent>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom
          sx={{ 
            fontWeight: 700,
            background: 'linear-gradient(45deg, #3b82f6, #10b981)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: 1
          }}
        >
          AWS Propuestas v3
        </Typography>
        
        <Typography 
          variant="subtitle1" 
          color="text.secondary"
          sx={{ marginBottom: 3 }}
        >
          Amazon Q Developer CLI Style
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', marginBottom: 2 }}>
          <CircularProgress 
            size={40} 
            thickness={4}
            sx={{ 
              color: 'primary.main',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }}
          />
        </Box>
        
        <StatusText variant="body2">
          {statusMessage}
        </StatusText>
        
        <ProgressContainer>
          <LinearProgress 
            variant="determinate" 
            value={progress}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
                background: 'linear-gradient(45deg, #3b82f6, #10b981)',
              }
            }}
          />
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ 
              display: 'block', 
              textAlign: 'center', 
              marginTop: 1 
            }}
          >
            {progress}% completado
          </Typography>
        </ProgressContainer>
      </LoadingContent>
      
      <Box 
        sx={{ 
          position: 'absolute', 
          bottom: 24, 
          textAlign: 'center',
          animation: `${fadeIn} 1.5s ease-out 1s both`,
        }}
      >
        <Typography variant="caption" color="text.secondary">
          Sistema inteligente de generación automática de propuestas AWS
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          6 MCPs especializados • IA integrada • Documentos profesionales
        </Typography>
      </Box>
    </LoadingContainer>
  );
};

export default LoadingScreen;
