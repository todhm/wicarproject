import purple from '@material-ui/core/colors/purple';

const drawerWidth = 240;

const styles = theme => ({
  root: {
    flexGrow: 1,
  },
  appFrame: {
    height: 430,
    zIndex: 1,
    overflow: 'hidden',
    position: 'relative',
    display: 'flex',
    width: '100%',
  },
  appBar: {
    width: `calc(100% - ${drawerWidth}px)`,
  },
  'appBar-left': {
    marginLeft: drawerWidth,
  },
  'appBar-right': {
    marginRight: drawerWidth,
  },
  drawerPaper: {
    position: 'relative',
    width: "100%",
    [theme.breakpoints.down('xs')]: {
      maxHeight:"150px",
   },
  },
  toolbar: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    backgroundColor: theme.palette.background.default,
    padding: theme.spacing.unit * 3,
  },
  drawerText:{
    paddingLeft:0 ,
    fontSize:20,
    fontWeight: 700,
    color:"#8f63f4",
    [theme.breakpoints.down('xs')]: {
      fontSize:8,
   },
   drawerItem:{
     [theme.breakpoints.down('xs')]: {
       padding:10,
    },
    dialogStyle:{
      minHeight:700,
    },
    margin: {
      margin: theme.spacing.unit ,
    },
    withoutLabel: {
      marginTop: theme.spacing.unit * 3,
    },
    textField: {
      flexBasis: 200,
    },
    noneBorderText:{
        border:"none",
    },
  }
},
topMarginSpace:{
    marginTop:theme.spacing.unit *5,
    marginBottom:theme.spacing.unit *5,
},
purpleButton: {
   color: theme.palette.getContrastText(purple[500]),
   marginTop: theme.spacing.unit * 5,
   width:"70%",
   backgroundColor: purple[500],
   '&:hover': {
     backgroundColor: purple[700],
   },
 },
marginCalendar:{
   [theme.breakpoints.down('xs')]: {
     marginLeft:16,
  },
 },
});
export const overlayStyle = {
    position: "relative",
    overflow: "hidden",
    direction: "ltr"
}
export const divStyle = {
    height: "140px"
}

export default styles;
