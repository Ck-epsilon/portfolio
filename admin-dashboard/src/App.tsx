// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** React-Admin application entry — ε-style admin dashboard.
 *
 *  Resources:
 *    /users  — User CRUD (requires admin:access permission for Edit)
 *    /items  — Items CRUD (generic CRUD for any collection)
 *
 *  Connected to api-starter FastAPI backend via JWT auth.
 */

import { Admin, Resource, CustomRoutes, Layout, AppBar, Menu } from "react-admin";
import { Route } from "react-router-dom";
import { Box, Typography } from "@mui/material";
import PeopleIcon from "@mui/icons-material/People";
import InventoryIcon from "@mui/icons-material/Inventory";
import DashboardIcon from "@mui/icons-material/Dashboard";

import { authProvider } from "./authProvider";
import { dataProvider } from "./dataProvider";
import { epsilonTheme, epsilonDarkTheme } from "./theme";
import { Dashboard } from "./resources/dashboard/Dashboard";
import {
  UserList,
  UserEdit,
  UserCreate,
  UserShow,
} from "./resources/users";
import {
  ItemList,
  ItemEdit,
  ItemCreate,
  ItemShow,
} from "./resources/items";

// ── ε-style AppBar ────────────────────────────────────────
const EpsilonAppBar = () => (
  <AppBar
    sx={{
      backgroundColor: "background.paper",
      color: "text.primary",
      boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
      "& .RaAppBar-title": {
        fontSize: 18,
        fontWeight: 700,
        letterSpacing: "-0.022em",
      },
    }}
  />
);

// ── ε-style Menu ──────────────────────────────────────────
const EpsilonMenu = () => (
  <Menu
    sx={{
      "& .RaMenuItemLink-root": {
        borderRadius: 2,
        mx: 0.5,
        "&.RaMenuItemLink-active": {
          backgroundColor: "rgba(0,113,227,0.08)",
          "& .RaMenuItemLink-icon": { color: "primary.main" },
        },
      },
    }}
  />
);

// ── ε-style Layout ────────────────────────────────────────
const EpsilonLayout = (props: any) => (
  <Layout {...props} appBar={EpsilonAppBar} menu={EpsilonMenu} />
);

// ── App ───────────────────────────────────────────────────
const App = () => (
  <Admin
    authProvider={authProvider}
    dataProvider={dataProvider}
    theme={epsilonTheme}
    darkTheme={epsilonDarkTheme}
    defaultTheme="light"
    layout={EpsilonLayout}
    dashboard={Dashboard}
    title="Admin"
  >
    {/* Custom routes */}
    <CustomRoutes>
      <Route path="/" element={
        <Box sx={{ p: 4 }}>
          <Typography variant="h4">Welcome</Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
            Select a resource from the sidebar to get started.
          </Typography>
        </Box>
      } />
    </CustomRoutes>

    {/* Resources */}
    <Resource
      name="users"
      list={UserList}
      edit={UserEdit}
      create={UserCreate}
      show={UserShow}
      icon={PeopleIcon}
    />
    <Resource
      name="items"
      list={ItemList}
      edit={ItemEdit}
      create={ItemCreate}
      show={ItemShow}
      icon={InventoryIcon}
    />
  </Admin>
);

export default App;
