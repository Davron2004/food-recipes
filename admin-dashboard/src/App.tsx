import { AuthProvider, Refine } from "@refinedev/core";
import dataProvider from "@refinedev/simple-rest";
import routerProvider from "@refinedev/react-router-v6";
import { useNotificationProvider, ThemedLayoutV2, ThemedSiderV2, ThemedTitleV2 } from "@refinedev/antd";
import { BrowserRouter, Outlet, Route, Routes, Link, Navigate } from "react-router-dom";

import { Fragment, useState } from "react";
import axios from "axios";

import { AuthActionResponse, CheckResponse, OnErrorResponse } from "@refinedev/core/dist/contexts/auth/types";

import { Content } from "antd/es/layout/layout";
import { Button, Menu, MenuProps } from "antd";

import "./App.css";
import { CreateRecipe, ListRecipes, ShowRecipe, EditRecipe } from "./pages/recipes/";
import { ListIngredient } from "./pages/ingredients";
import { Login, LoginModal } from "./pages/login";
import { AppActivationsList, CreateAppActivation } from "./pages/app-activations/";
import { API_URL } from "./providers/data-provider";


export function updateToken(token: string) {
  axiosInstance.defaults.headers['Authorization'] = `Bearer ${token}`;
}

export const axiosInstance = axios.create();
updateToken(localStorage.getItem('token') || '');

const customDataProvider = dataProvider(API_URL, axiosInstance);

const customAuthProvider: AuthProvider = {
  login: async (params: any): Promise<AuthActionResponse> => {
    const { username, password } = params;
    try {
      const response = await axiosInstance.post('/login', { username, password });
      localStorage.setItem('token', response.data.token);
      updateToken(response.data.token);
      return {
        ...response.data,
        success: true
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error as Error
      };
    }
  },
  logout: async (params: any): Promise<AuthActionResponse> => {
    localStorage.removeItem('token');
    updateToken('');
    return {
      success: true,
      redirectTo: "/login"
    };
  },
  check: async (params?: any): Promise<CheckResponse> => {
    const token = localStorage.getItem('token');
    if (token) {
      return {
        authenticated: true,
      };
    }
    return {
      authenticated: false,
      redirectTo: "/login",
    };
  },
  onError: async (error: any): Promise<OnErrorResponse> => {
    return {
      error,
    };
  }
}

function App() {
  const [isLoginModalVisible, setLoginModalVisible] = useState(false);

  const showLoginModal = () => setLoginModalVisible(true);
  const hideLoginModal = () => setLoginModalVisible(false);

  axiosInstance.interceptors.response.use(
    response => response,
    error => {
      if (error.response && (error.response.status === 401 || error.response.status === 422)) {
        if (!isLoginModalVisible) {
          localStorage.removeItem('token');
          updateToken('');
          showLoginModal();
        }
      }
      return Promise.reject(error);
    }
  );

  return (
    <BrowserRouter basename="/manage">
      <Refine
        dataProvider={customDataProvider}
        notificationProvider={useNotificationProvider}
        routerProvider={routerProvider}
        authProvider={customAuthProvider}
        options={{
          disableTelemetry: true
        }}
        resources={[
          {
            name: "recipes",
            list: "/recipes",
            show: "/recipes/:id",
            create: "/recipes/new",
            edit: "/recipes/edit/:id",
            options: {
              label: "Recipes"
            }
          },
          {
            name: "ingredients",
            list: "/ingredients",
            options: {
              label: "Ingredients"
            }

          },
          {
            name: "auth/app-activations",
            list: "/activation",
            options: {
              label: "App activations"
            }
          }
        ]}
      >
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Navigate to="/recipes" />} />
          <Route element={
            <ThemedLayoutV2
              Sider={() => (
                <ThemedSiderV2
                  Title={({ collapsed }) => (
                    <ThemedTitleV2
                      collapsed={collapsed}
                      // icon={collapsed ? <SMALL_ICON/> : <LARGE_ICON/>}
                      text={collapsed ? "" : "Food Recipes"}
                    />
                  )}
                  render={({ items, logout, collapsed }) => {
                    const menuItems: MenuProps['items'] = [
                      {
                        key: "/recipes/new",
                        label: (
                          <Link to="/recipes/new">
                            Create New Recipe
                          </Link>
                        ),
                      },
                      {
                        key: "/activation/new",
                        label: (
                          <Link to="/activation/new">
                            Create app activation
                          </Link>
                        ),
                      },
                    ];
                    return (
                      <>
                        {items}
                        {logout}
                        <Menu items={menuItems} />
                      </>
                    );
                  }}
                />
              )}>
              <Content>
                <div
                  style={{
                    padding: 24,
                    minHeight: 360,
                  }}
                >
                  <Outlet />
                </div>
              </Content>
            </ThemedLayoutV2>}>
            <Route path="/recipes" element={<ListRecipes />} />
            <Route path="/recipes/:id" element={<ShowRecipe />} />
            <Route path="/recipes/new" element={<CreateRecipe />} />
            <Route path="/recipes/edit/:id" element={<EditRecipe />} />
            <Route path="/ingredients" element={<ListIngredient />} />
            <Route path="/activation" element={<AppActivationsList />} />
            <Route path="/activation/new" element={<CreateAppActivation />} />
          </Route>
        </Routes>
        <LoginModal visible={isLoginModalVisible} onClose={hideLoginModal} />
      </Refine>
    </BrowserRouter>
  );
}

export default App;