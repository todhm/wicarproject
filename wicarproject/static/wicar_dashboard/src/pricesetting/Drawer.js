import React from 'react';
import {
    Grid,
    ListItem,
    ListItemText,
    IconButton,
    Drawer,
    Divider,
    List,
    ListItemIcon
} from '@material-ui/core'
import styles from '../utils/styles/styles'
import {withStyles} from '@material-ui/core/styles';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import {Home, Language} from '@material-ui/icons';
import {Link} from 'react-router-dom';
import compose from 'recompose/compose';

const DrawerList = (props) => {
    const {classes,carId} = props;
    let linkList = [
        {link:"/car_setting/price_setting",label:"대여가격설정"},
        {link:"/car_setting/vacation_setting",label:"대여날짜설정"},
        {link:"/car_setting/basic_setting",label:"차량기본설정"},
        {link:"/car_setting/option_setting",label:"차량옵션설정"},
        {link:"/car_setting/photo_setting",label:"차량사진설정"},
    ];
    linkList = linkList.map((obj)=>({...obj,link:obj.link + "/" + carId}))

    return (
        <Drawer
               variant="permanent"
               classes={{
                 paper: classes.drawerPaper,
               }}
               anchor={"left"}
             >
               <div className={classes.toolbar} />
               <List>
                    <Grid container>
                        {linkList.map((link)=>
                            <Grid item xs={4} sm={12} key={link.label}>
                                <Link to={link.link} >
                                    <ListItem className={classes.drawerItem}>
                                        <ListItemText classes={{primary:classes.drawerText}}  primary={link.label}/>
                                    </ListItem>
                                </Link>
                            </Grid>
                        )}
                    </Grid>
               </List>
         </Drawer>
        );
}


export default withStyles(styles)(DrawerList);
