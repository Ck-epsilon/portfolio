// Author: Ck.epsilon & Chaos (AI Programming Assistant)
/** Items CRUD (generic "items" resource from api-starter /items endpoints). */

import {
  List,
  Datagrid,
  TextField,
  EditButton,
  ShowButton,
  TextInput,
  Edit,
  SimpleForm,
  Create,
  Show,
  SimpleShowLayout,
} from "react-admin";

const itemFilters = [<TextInput source="q" label="Search" alwaysOn key="search" />];

export const ItemList = () => (
  <List filters={itemFilters}>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <TextField source="created_at" />
      <EditButton />
      <ShowButton />
    </Datagrid>
  </List>
);

export const ItemEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" multiline />
    </SimpleForm>
  </Edit>
);

export const ItemCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="description" multiline />
    </SimpleForm>
  </Create>
);

export const ItemShow = () => (
  <Show>
    <SimpleShowLayout>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="description" />
      <TextField source="created_at" />
    </SimpleShowLayout>
  </Show>
);
