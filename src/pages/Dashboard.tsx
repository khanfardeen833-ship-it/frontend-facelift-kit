import { Users, UserCheck, Calendar, TrendingUp } from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
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

export default function Dashboard() {
  // Mock data - replace with your API calls
  const recentEmployees = [
    {
      id: 1,
      name: "John Doe",
      department: "Engineering",
      position: "Senior Developer",
      status: "Active",
    },
    {
      id: 2,
      name: "Jane Smith",
      department: "Marketing",
      position: "Marketing Manager",
      status: "Active",
    },
    {
      id: 3,
      name: "Mike Johnson",
      department: "Sales",
      position: "Sales Executive",
      status: "Active",
    },
    {
      id: 4,
      name: "Sarah Williams",
      department: "HR",
      position: "HR Specialist",
      status: "On Leave",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Welcome back! Here's an overview of your workforce.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Employees"
          value="1,234"
          change="+12% from last month"
          changeType="positive"
          icon={Users}
          iconColor="bg-primary"
        />
        <StatCard
          title="Present Today"
          value="1,156"
          change="93.7% attendance"
          changeType="positive"
          icon={UserCheck}
          iconColor="bg-success"
        />
        <StatCard
          title="On Leave"
          value="45"
          change="3.6% of workforce"
          changeType="neutral"
          icon={Calendar}
          iconColor="bg-warning"
        />
        <StatCard
          title="New Hires"
          value="23"
          change="+5 this week"
          changeType="positive"
          icon={TrendingUp}
          iconColor="bg-accent"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="shadow-card">
          <CardHeader>
            <CardTitle>Recent Employees</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Position</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentEmployees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell className="font-medium">
                      {employee.name}
                    </TableCell>
                    <TableCell>{employee.department}</TableCell>
                    <TableCell>{employee.position}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          employee.status === "Active"
                            ? "default"
                            : "secondary"
                        }
                      >
                        {employee.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Departments</span>
              <span className="text-2xl font-bold">12</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Pending Leave Requests</span>
              <span className="text-2xl font-bold text-warning">8</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Open Positions</span>
              <span className="text-2xl font-bold text-primary">5</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Avg. Employee Tenure</span>
              <span className="text-2xl font-bold">3.2 yrs</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
