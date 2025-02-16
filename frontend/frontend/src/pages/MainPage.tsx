// import React, { useState } from 'react';
// import {
//   AppBar,
//   Toolbar,
//   Typography,
//   Box,
//   Card,
//   CardContent,
// } from '@mui/material';
// import { styled } from '@mui/material/styles';

// /**
//  * FANCY DIAMOND PROGRESS COMPONENT
//  * Uses a gradient stroke with a subtle glow.
//  */
// function DiamondProgress({ value = 0, size = 300, strokeWidth = 10 }) {
//   // Clamp value between 0–100
//   const clampedValue = Math.min(100, Math.max(0, value));

//   // Each side of the diamond is ~70.71; total perimeter ~282.84
//   const DIAMOND_PERIMETER = 4 * Math.sqrt(50 ** 2 + 50 ** 2);
//   // strokeDashoffset controls how much of the stroke is NOT shown
//   const offset = DIAMOND_PERIMETER - (DIAMOND_PERIMETER * clampedValue) / 100;

//   return (
//     <Box sx={{ width: size, height: size, mx: 'auto' }}>
//       <svg
//         width="100%"
//         height="100%"
//         viewBox="0 0 100 100"
//         style={{ overflow: 'visible' }}
//       >
//         {/* DEFINITIONS: gradient + glow filter */}
//         <defs>
//           {/* Linear gradient from top-left (#FF6CAB) to bottom-right (#7366FF) */}
//           <linearGradient id="diamondGradient" x1="0" y1="0" x2="1" y2="1">
//             <stop offset="0%" stopColor="#FF6CAB" />
//             <stop offset="100%" stopColor="#7366FF" />
//           </linearGradient>

//           {/* Glow filter */}
//           <filter id="diamondGlow" x="-50%" y="-50%" width="200%" height="200%">
//             {/* Blur the shape */}
//             <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
//             {/* Merge the blur with the original stroke to create a glow */}
//             <feMerge>
//               <feMergeNode in="blur" />
//               <feMergeNode in="SourceGraphic" />
//             </feMerge>
//           </filter>
//         </defs>

//         {/* Background stroke (light gray) */}
//         <path
//           d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
//           fill="none"
//           stroke="#ccc"
//           strokeWidth={strokeWidth}
//           strokeLinejoin="round"
//           strokeLinecap="round"
//         />

//         {/* Foreground stroke (gradient + glow) */}
//         <path
//           d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
//           fill="none"
//           stroke="url(#diamondGradient)"   // Apply the linear gradient
//           strokeWidth={strokeWidth}
//           strokeLinejoin="round"
//           strokeLinecap="round"
//           strokeDasharray={DIAMOND_PERIMETER}
//           strokeDashoffset={offset}
//           filter="url(#diamondGlow)"        // Apply the glow filter
//           style={{
//             transition: 'stroke-dashoffset 0.4s ease',
//           }}
//         />
//       </svg>
//     </Box>
//   );
// }

// /** 
//  * MAIN CONTENT STYLING
//  * Enough padding so content isn't hidden under the AppBar.
//  */
// const MainContent = styled('main')(({ theme }) => ({
//   padding: theme.spacing(2),
//   marginTop: theme.mixins.toolbar.minHeight,
  
// }));

// /**
//  * DASHBOARD COMPONENT
//  * Has a top AppBar, one dummy card, and a DiamondProgress card (fancy).
//  */
// function Dashboard() {
//   // Track numeric progress (0–100)
//   const [progress, setProgress] = useState(25);

//   const handleIncrease = () => setProgress((prev) => Math.min(100, prev + 25));
//   const handleDecrease = () => setProgress((prev) => Math.max(0, prev - 25));

//   return (
//     <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
//       {/* TOP APP BAR (no sidebar) */}
//       <AppBar position="fixed">
//         <Toolbar>
//           <Typography variant="h6" noWrap component="div">
//             My Dashboard
//           </Typography>
//         </Toolbar>
//       </AppBar>

//       {/* MAIN CONTENT AREA */}
//       <MainContent>
//         {/* <Typography variant="h4" gutterBottom>
//           Welcome to the Dashboard
//         </Typography> */}

//         <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
//           {/* Dummy Card #1 */}
//           <Card elevation={0} sx={{ width: 300 }}>
//             <CardContent>
//               <Typography variant="h6">Card 1</Typography>
//               <Typography variant="body2" color="text.secondary">
//                 This is a dummy card. Put stats, charts, or any content here.
//               </Typography>
//             </CardContent>
//           </Card>

//           {/* Fancy Diamond Progress Card */}
//           <Card elevation={0} sx={{ width: 900, height: 650, textAlign: 'center', p: 2 }}>
//             <CardContent>
//                 {/* <Typography variant="h4" gutterBottom>
//                 Diamond Progress
//                 </Typography> */}
//               <DiamondProgress value={progress} />
//               {/* <Typography variant="h6" sx={{ mt: 2 }}>
//                 Current progress: {progress}%
//               </Typography> */}
//               <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
//                 <Box
//                   sx={{
//                     p: 1,
//                     backgroundColor: '#ccc',
//                     borderRadius: 1,
//                     cursor: 'pointer',
//                     '&:hover': { backgroundColor: '#bbb' },
//                   }}
//                   onClick={handleDecrease}
//                 >
//                   Decrease
//                 </Box>
//                 <Box
//                   sx={{
//                     p: 1,
//                     backgroundColor: '#ccc',
//                     borderRadius: 1,
//                     cursor: 'pointer',
//                     '&:hover': { backgroundColor: '#bbb' },
//                   }}
//                   onClick={handleIncrease}
//                 >
//                   Increase
//                 </Box>
//               </Box>
//             </CardContent>
//           </Card>
//         </Box>
//       </MainContent>
//     </Box>
//   );
// }

// export default Dashboard;


import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import { styled } from '@mui/material/styles';

/**
 * FANCY DIAMOND PROGRESS COMPONENT
 * Uses a gradient stroke with a subtle glow.
 */
function DiamondProgress({ value = 0, size = 300, strokeWidth = 10 }) {
  // Clamp value between 0–100
  const clampedValue = Math.min(100, Math.max(0, value));

  // Each side of the diamond is ~70.71; total perimeter ~282.84
  const DIAMOND_PERIMETER = 4 * Math.sqrt(50 ** 2 + 50 ** 2);
  // strokeDashoffset controls how much of the stroke is NOT shown
  const offset = DIAMOND_PERIMETER - (DIAMOND_PERIMETER * clampedValue) / 100;

  return (
    <Box sx={{ width: size, height: size, mx: 'auto' }}>
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 100 100"
        style={{ overflow: 'visible' }}
      >
        {/* DEFINITIONS: gradient + glow filter */}
        <defs>
          {/* Linear gradient from top-left (#FF6CAB) to bottom-right (#7366FF) */}
          <linearGradient id="diamondGradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#FF6CAB" />
            <stop offset="100%" stopColor="#7366FF" />
          </linearGradient>

          {/* Glow filter */}
          <filter id="diamondGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Background stroke (light gray) */}
        <path
          d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
          fill="none"
          stroke="#ccc"
          strokeWidth={strokeWidth}
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Foreground stroke (gradient + glow) */}
        <path
          d="M 50,0 L 100,50 L 50,100 L 0,50 Z"
          fill="none"
          stroke="url(#diamondGradient)" // Apply the linear gradient
          strokeWidth={strokeWidth}
          strokeLinejoin="round"
          strokeLinecap="round"
          strokeDasharray={DIAMOND_PERIMETER}
          strokeDashoffset={offset}
          filter="url(#diamondGlow)" // Apply the glow filter
          style={{
            transition: 'stroke-dashoffset 0.4s ease',
          }}
        />
      </svg>
    </Box>
  );
}

/** 
 * MAIN CONTENT STYLING
 * Provides padding and positions content below the AppBar.
 */
const MainContent = styled('main')(({ theme }) => ({
  padding: theme.spacing(2),
  marginTop: theme.mixins.toolbar.minHeight,
}));

/**
 * PAGE CONTAINER
 * A full-page wrapper that applies the background color to the entire viewport.
 */
const PageContainer = styled('div')({
  width: '100vw',
  minHeight: '100vh',
  backgroundColor: '#081c4a', // Your desired background color
});

/**
 * DASHBOARD COMPONENT
 * Contains a top AppBar, a dummy card, and a Fancy DiamondProgress card.
 * Everything is wrapped in PageContainer.
 */
function Dashboard() {
  // Track numeric progress (0–100)
  const [progress, setProgress] = useState(25);

  const handleIncrease = () => setProgress((prev) => Math.min(100, prev + 25));
  const handleDecrease = () => setProgress((prev) => Math.max(0, prev - 25));

  return (
    <PageContainer>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* TOP APP BAR */}
        <AppBar position="fixed" sx={{ backgroundColor: '#081c4a', boxShadow: 'none' }}>
          <Toolbar>
            <Typography variant="h6" noWrap component="div" sx={{ color: '#081c4a' }}>
              My Dashboard
            </Typography>
          </Toolbar>
        </AppBar>

        {/* MAIN CONTENT AREA */}
        <MainContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            {/* Dummy Card with matching background */}
            <Card elevation={0} sx={{ width: 300, backgroundColor: '#081c4a' }}>
              <CardContent>
                <Typography variant="h6" sx={{ color: '#FFFFFF' }}>
                  Card 1
                </Typography>
                <Typography variant="body2" sx={{ color: '#FFFFFF' }}>
                  This is a dummy card. Put stats, charts, or any content here.
                </Typography>
              </CardContent>
            </Card>

            {/* Fancy Diamond Progress Card */}
            <Card
              elevation={0}
              sx={{
                width: 900,
                height: 650,
                textAlign: 'center',
                p: 2,
                backgroundColor: '#081c4a',
              }}
            >
              <CardContent>
                <DiamondProgress value={progress} />
                <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
                  <Box
                    sx={{
                      p: 1,
                      backgroundColor: '#ccc',
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: '#bbb' },
                      color: '#081c4a',
                    }}
                    onClick={handleDecrease}
                  >
                    Decrease
                  </Box>
                  <Box
                    sx={{
                      p: 1,
                      backgroundColor: '#ccc',
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: '#bbb' },
                      color: '#081c4a',
                    }}
                    onClick={handleIncrease}
                  >
                    Increase
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </MainContent>
      </Box>
    </PageContainer>
  );
}

export default Dashboard;
