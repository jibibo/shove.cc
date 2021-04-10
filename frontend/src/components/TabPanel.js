import Box from "@material-ui/core/Box";
import Typography from "@material-ui/core/Typography";

import React, { useEffect } from 'react'

export default function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
        <div
            hidden={value !== index}
        >
            {value === index && (
                <Box p={3}>
                    <Typography>{children}</Typography>
                </Box>
            )}
        </div>
    );
}
