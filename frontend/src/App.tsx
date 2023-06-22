import React from 'react'
import IconButton from '@mui/material/IconButton'
import Close from '@mui/icons-material/Close'
import { SnackbarProvider, SnackbarKey, useSnackbar } from 'notistack'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Workflow from './components/Project'
import Layout from 'components/Layout'
import Dashboard from 'pages/Dashboard'
import AccountManager from 'pages/AccountManager'
import Account from 'pages/Account'
import AccountDelete from 'pages/AccountDelete'
import Projects from './pages/Projects'
import Database from './pages/Database'
import Login from 'pages/Login'
import ProjectFormComponent from "./pages/Projects/Create";
import ResetPassword from "./pages/ResetPassword";

const App: React.FC = () => {
  return (
    <SnackbarProvider
      maxSnack={5}
      action={(snackbarKey) => (
        <SnackbarCloseButton snackbarKey={snackbarKey} />
      )}
    >
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects/workflow" element={<Workflow />} />
            <Route path="/account-manager" element={<AccountManager />} />
            <Route path="/account" element={<Account />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/database" element={<Database />} />
            <Route path="/login" element={<Login />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/account-deleted" element={<AccountDelete />} />
            <Route path="/projects/new-project" element={<ProjectFormComponent />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </SnackbarProvider>
  )
}

const SnackbarCloseButton: React.FC<{ snackbarKey: SnackbarKey }> = ({
  snackbarKey,
}) => {
  const { closeSnackbar } = useSnackbar()
  return (
    <IconButton onClick={() => closeSnackbar(snackbarKey)} size="large">
      <Close style={{ color: 'white' }} />
    </IconButton>
  )
}

export default App
