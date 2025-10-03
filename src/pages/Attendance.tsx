import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Attendance() {
  // Mock data - replace with your API calls
  const todayAttendance = [
    {
      id: 1,
      name: "John Doe",
      checkIn: "09:00 AM",
      checkOut: "06:00 PM",
      status: "Present",
    },
    {
      id: 2,
      name: "Jane Smith",
      checkIn: "08:45 AM",
      checkOut: "05:30 PM",
      status: "Present",
    },
    {
      id: 3,
      name: "Mike Johnson",
      checkIn: "09:15 AM",
      checkOut: "-",
      status: "Present",
    },
    {
      id: 4,
      name: "Sarah Williams",
      checkIn: "-",
      checkOut: "-",
      status: "On Leave",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Attendance</h1>
        <p className="text-muted-foreground mt-2">
          Track and manage employee attendance records
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="shadow-card lg:col-span-2">
          <CardHeader>
            <CardTitle>Today's Attendance</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Check In</TableHead>
                  <TableHead>Check Out</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {todayAttendance.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell className="font-medium">{record.name}</TableCell>
                    <TableCell>{record.checkIn}</TableCell>
                    <TableCell>{record.checkOut}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          record.status === "Present" ? "default" : "secondary"
                        }
                      >
                        {record.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Calendar</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-center">
              <Calendar mode="single" className="rounded-md border" />
            </CardContent>
          </Card>

          <Card className="shadow-card">
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Present</span>
                <span className="text-2xl font-bold text-success">1,156</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Absent</span>
                <span className="text-2xl font-bold text-destructive">33</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">On Leave</span>
                <span className="text-2xl font-bold text-warning">45</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Attendance Rate</span>
                <span className="text-2xl font-bold text-primary">93.7%</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
