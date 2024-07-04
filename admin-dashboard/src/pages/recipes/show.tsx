import { useParams } from "react-router-dom";
import { useOne, useApiUrl } from "@refinedev/core";

import { Show } from "@refinedev/antd";
import { Typography, List, Space, Image } from "antd";

const { Title, Text } = Typography;

export const ShowRecipe = () => {
    const { id } = useParams();
    const { data, isLoading } = useOne({
        resource: "recipes",
        id: id,
    });
    const recipe = data?.data;
    const apiUrl = useApiUrl();

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <Show>
            <Space align="baseline">
                <Title level={2}>{recipe?.name}</Title>
                <Text>({recipe?.category?.name})</Text>
            </Space>
            <br />
            <Text>{recipe?.instructions}</Text>
            <Title level={4}>Ingredients</Title>
            <List
                dataSource={recipe?.ingredients}
                renderItem={(ingredient: any) => (
                    <p>{ingredient.ingredient.name} - {`${ingredient.qty} ${ingredient.unit}`}</p>
                )}
            />
            <Title level={4}>Pictures</Title>
            <List
                grid={{ gutter: 16, column: 4 }}
                dataSource={recipe?.pictures}
                renderItem={(pic_id: any) => (
                    <List.Item>
                        <Image src={`${apiUrl}/pictures/${pic_id}`} alt="Recipe" />
                    </List.Item>
                )}
            />
        </Show>
    );
};