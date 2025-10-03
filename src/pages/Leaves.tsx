import { Plus, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function Leaves() {
  // Mock data - replace with your API calls
  const leaveRequests = [
    {
      id: 1,
      employee: "John Doe",
      type: "Annual Leave",
      from: "2024-01-15",
      to: "2024-01-20",
      days: 5,
      status: "Pending",
      reason: "Family vacation",
    },
    {
      id: 2,
      employee: "Jane Smith",
      type: "Sick Leave",
      from: "2024-01-10",
      to: "2024-01-12",
      days: 2,
      status: "Approved",
      reason: "Medical treatment",
    },
    {
      id: 3,
      employee: "Mike Johnson",
      type: "Annual Leave",
      from: "2024-02-01",
      to: "2024-02-07",
      days: 6,
      status: "Pending",
      reason: "Personal travel",
    },
    {
      id: 4,
      employee: "Sarah Williams",
      type: "Maternity Leave",
      from: "2024-01-05",
      to: "2024-04-05",
      days: 90,
      status: "Approved",
      reason: "Maternity",
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Approved":
        return "default";
      case "Pending":
        return "secondary";
      case "Rejected":
        return "destructive";
      default:
        return "secondary";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Leave Management</h1>
          <p className="text-muted-foreground mt-2">
            Manage employee leave requests and approvals
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          New Leave Request
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <Card className="shadow-card">
          <CardContent className="p-6">
            <p className="text-sm font-medium text-muted-foreground">Pending</p>
            <h3 className="text-3xl font-bold mt-2">8</h3>
          </CardContent>
        </Card>
        <Card className="shadow-card">
          <CardContent className="p-6">
            <p className="text-sm font-medium text-muted-foreground">Approved</p>
            <h3 className="text-3xl font-bold mt-2 text-success">45</h3>
          </CardContent>
        </Card>
        <Card className="shadow-card">
          <CardContent className="p-6">
            <p className="text-sm font-medium text-muted-foreground">Rejected</p>
            <h3 className="text-3xl font-bold mt-2 text-destructive">3</h3>
          </CardContent>
        </Card>
        <Card className="shadow-card">
          <CardContent className="p-6">
            <p className="text-sm font-medium text-muted-foreground">This Month</p>
            <h3 className="text-3xl font-bold mt-2">56</h3>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Leave Requests</CardTitle>
            <Button variant="outline" className="gap-2">
              <Filter className="h-4 w-4" />
              Filters
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>From</TableHead>
                <TableHead>To</TableHead>
                <TableHead>Days</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {leaveRequests.map((request) => (
                <TableRow key={request.id}>
                  <TableCell className="font-medium">
                    {request.employee}
                  </TableCell>
                  <TableCell>{request.type}</TableCell>
                  <TableCell>
                    {new Date(request.from).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {new Date(request.to).toLocaleDateString()}
                  </TableCell>
                  <TableCell>{request.days}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {request.reason}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(request.status) as any}>
                      {request.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
