import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";

export default function Settings() {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage your application settings and preferences
        </p>
      </div>

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Company Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="company-name">Company Name</Label>
              <Input id="company-name" placeholder="Enter company name" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="company-email">Email</Label>
              <Input
                id="company-email"
                type="email"
                placeholder="company@example.com"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="company-address">Address</Label>
            <Input id="company-address" placeholder="Enter company address" />
          </div>
          <Button>Save Changes</Button>
        </CardContent>
      </Card>

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Attendance Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto Check-out</Label>
              <p className="text-sm text-muted-foreground">
                Automatically check out employees at end of day
              </p>
            </div>
            <Switch />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Late Arrival Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Send notifications for late arrivals
              </p>
            </div>
            <Switch />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="work-start">Work Start Time</Label>
              <Input id="work-start" type="time" defaultValue="09:00" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="work-end">Work End Time</Label>
              <Input id="work-end" type="time" defaultValue="18:00" />
            </div>
          </div>
          <Button>Save Changes</Button>
        </CardContent>
      </Card>

      <Card className="shadow-card">
        <CardHeader>
          <CardTitle>Leave Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="annual-leave">Annual Leave Days</Label>
              <Input
                id="annual-leave"
                type="number"
                defaultValue="20"
                min="0"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sick-leave">Sick Leave Days</Label>
              <Input
                id="sick-leave"
                type="number"
                defaultValue="10"
                min="0"
              />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto-approve Leave</Label>
              <p className="text-sm text-muted-foreground">
                Automatically approve leave requests
              </p>
            </div>
            <Switch />
          </div>
          <Button>Save Changes</Button>
        </CardContent>
      </Card>
    </div>
  );
}
