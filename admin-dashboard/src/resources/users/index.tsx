// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** User list with search, sort, and role-aware actions. */

import {
  List,
  Datagrid,
  TextField,
  EmailField,
  BooleanField,
  EditButton,
  ShowButton,
  TextInput,
  Edit,
  SimpleForm,
  TextInput as RaTextInput,
  BooleanInput,
  Create,
  Show,
  SimpleShowLayout,
  usePermissions,
} from "react-admin";

const userFilters = [
  <TextInput source="q" label="Search" alwaysOn key="search" />,
];

export const UserList = () => {
  const { permissions } = usePermissions();
  return (
    <List filters={userFilters}>
      <Datagrid rowClick="show">
        <TextField source="id" />
        <TextField source="username" />
        <EmailField source="email" />
        <BooleanField source="is_active" />
        {permissions?.includes("admin:access") && <EditButton />}
        <ShowButton />
      </Datagrid>
    </List>
  );
};

export const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <RaTextInput source="username" />
      <TextInput source="email" type="email" />
      <BooleanInput source="is_active" />
    </SimpleForm>
  </Edit>
);

export const UserCreate = () => (
  <Create>
    <SimpleForm>
      <RaTextInput source="username" />
      <TextInput source="email" type="email" />
      <RaTextInput source="password" type="password" />
    </SimpleForm>
  </Create>
);

export const UserShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="username" />
      <EmailField source="email" />
      <BooleanField source="is_active" />
      <TextField source="created_at" />
    </SimpleShowLayout>
  </Show>
);
