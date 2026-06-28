// Author: Ck.epsilon
/** Shared types for Order domain. */

export interface Order {
  id: string;
  customer: string;
  amount: number;
  status: 'completed' | 'pending' | 'cancelled';
  date: string;
}

export interface OrderFormValues {
  customer: string;
  amount: number;
  status: Order['status'];
}
