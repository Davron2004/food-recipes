import { useState, useEffect } from 'react';
import { useApiUrl, useList } from '@refinedev/core';

import { Table, List, Space, Select, Switch } from 'antd';
import { DeleteButton, EditButton, ShowButton, useSelect } from '@refinedev/antd';
import { Category, RecipeExtended } from '../../interfaces';
import { axiosInstance } from '../../App';

export const ListRecipes = () => {
  const { selectProps: catProps } = useSelect<Category>({ resource: "categories", optionLabel: "name" });
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [filteredRecipes, setFilteredRecipes] = useState<RecipeExtended[]>([]);
  const [loadingSwitches, setLoadingSwitches] = useState<{ [key: number]: boolean }>({});
  const apiUrl = useApiUrl();

  const { data, error, isLoading, refetch } = useList<RecipeExtended>({ 
    resource: "recipes",
    config: {
      pagination: {
        current: pagination.current,
        pageSize: pagination.pageSize,
      }
    },
  });

  const [recipes, setRecipes] = useState<RecipeExtended[]>([]);

  useEffect(() => {
    if (data?.data) {
      const sortedRecipes = [...data.data].sort((a: RecipeExtended, b: RecipeExtended) => a.created_at.localeCompare(b.created_at));
      setRecipes(sortedRecipes);
    }
  }, [data]);

  useEffect(() => {
    if (recipes.length > 0) {
      if (selectedCategories.length === 0) {
        setFilteredRecipes(recipes);
        return;
      }
      const filtered = recipes.filter(recipe => 
        selectedCategories.includes(recipe.category.id)
      );
      setFilteredRecipes(filtered);
    }
  }, [recipes, selectedCategories]);

  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    return <div>Error: {error.message}</div>;
  }

  const onChangeDemoSwitch = async (
    checked: boolean, event: React.MouseEvent<HTMLButtonElement, MouseEvent>, rec_id: number) => {
      event.preventDefault();
      setLoadingSwitches(prev => ({ ...prev, [rec_id]: true }));
      await axiosInstance.put(`${apiUrl}/recipes/${rec_id}/change-auth`, {
        needs_auth: !checked
      }, {
        headers: {
          "Authorization": "Bearer " + (localStorage.getItem("token") as string)
        }
      });
      setLoadingSwitches(prev => ({ ...prev, [rec_id]: false }));
      refetch();
    }
  
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: '40%',
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: '30%',
      render: (category: Category) => category.name,
      filterDropdown: () => (
        // @ts-ignore
        <Select<number[]>
          style={{ minWidth: 200 }}
          mode='multiple'
          placeholder='Select categories'
          {...catProps}
          value={selectedCategories}
          onChange={setSelectedCategories}
        />
      ),
    },
    {
      title: 'Actions',
      width: '30%',
      render: (recipe: RecipeExtended) => (
        <Space>
          <EditButton resource="recipes" recordItemId={recipe.id} hideText />
          <ShowButton resource="recipes" recordItemId={recipe.id} hideText />
          <DeleteButton resource="recipes" recordItemId={recipe.id} hideText />
          <Switch 
            checkedChildren="Demo"
            unCheckedChildren="Auth"
            checked={!recipe.needs_auth}
            loading={loadingSwitches[recipe.id]}
            onChange={(checked, event) => onChangeDemoSwitch(checked, event, recipe.id)}
          />
        </Space>
      ),
    }
  ];

  const handleTableChange = (pagination: any) => {
    setPagination(pagination);
  };
  
  return (
    <List>
      <Table 
        title={() => `Total amount: ${filteredRecipes.length}`} 
        dataSource={[...filteredRecipes].reverse()} 
        columns={columns} 
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: filteredRecipes.length,
          position: ['topRight'],
        }}
        onChange={handleTableChange}
      />
    </List>
  );
};