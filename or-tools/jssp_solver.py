import collections
from ortools.sat.python import cp_model

def solve_simple_jssp():
    """Solves a simple Job Shop Scheduling Problem using CP-SAT."""

    # --- 1. Data Definition ---
    # Define the jobs. Each job is a list of tasks.
    # Each task is represented as a tuple: (machine_id, processing_time)
    # The order of tasks in the list defines the sequence they must follow within the job.
    jobs_data = [
        # Job 0: Task 0 (Machine 0, 3 time units), Task 1 (Machine 1, 2 time units), Task 2 (Machine 2, 2 time units)
        [(0, 3), (1, 2), (2, 2)],
        # Job 1: Task 0 (Machine 0, 2 time units), Task 1 (Machine 2, 1 time unit), Task 2 (Machine 1, 4 time units)
        [(0, 2), (2, 1), (1, 4)],
        # Job 2: Task 0 (Machine 1, 4 time units), Task 1 (Machine 2, 3 time units)
        [(1, 4), (2, 3)]
    ]

    num_jobs = len(jobs_data)
    all_jobs = range(num_jobs)

    # Calculate the number of machines based on the maximum machine_id mentioned in jobs_data
    # This ensures we account for all machines used in the problem.
    max_machine_id = 0
    for job in jobs_data:
        for task in job:
            if task[0] > max_machine_id:
                max_machine_id = task[0]
    num_machines = max_machine_id + 1
    all_machines = range(num_machines)

    print(f"Problem Data:")
    print(f"  Number of Jobs: {num_jobs}")
    print(f"  Number of Machines: {num_machines}")
    for i, job in enumerate(jobs_data):
        print(f"  Job {i}: {job}")
    print("-" * 30)

    # --- 2. Model Creation ---
    # Instantiate the CP-SAT model.
    model = cp_model.CpModel()

    # --- 3. Define Variables ---

    # Calculate a maximum possible schedule length (horizon).
    # Summing all processing times provides a safe, though potentially loose, upper bound.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Dictionary to store all task interval variables.
    # Key: (job_id, task_index)
    # Value: tuple (start_var, end_var, interval_var)
    all_tasks = {}

    # Dictionary to store lists of interval variables for each machine.
    # This is needed for the NoOverlap constraint.
    # Key: machine_id
    # Value: list of interval variables assigned to that machine
    machine_to_intervals = collections.defaultdict(list)

    # Create interval variables for each task in each job.
    for job_id in all_jobs:
        for task_index, (machine_id, duration) in enumerate(jobs_data[job_id]):
            # Create a unique suffix for variable names for easier debugging.
            suffix = f'_{job_id}_{task_index}'

            # Create the start time variable for the task.
            # It can start anytime between 0 and the horizon.
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            # Create the end time variable for the task.
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            # Create the interval variable. This links start, duration, and end.
            # The duration is fixed based on the input data.
            interval_var = model.NewIntervalVar(start_var, duration, end_var, 'interval' + suffix)

            # Store the created variables for later reference.
            all_tasks[(job_id, task_index)] = (start_var, end_var, interval_var)
            # Add this task's interval variable to the list for the machine it runs on.
            machine_to_intervals[machine_id].append(interval_var)

    # --- 4. Define Constraints ---

    # a) No Overlap Constraint:
    # For each machine, ensure that the intervals of tasks assigned to it do not overlap in time.
    # This enforces that a machine can only process one task at a time.
    for machine_id in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine_id])
        # print(f"Debug: Machine {machine_id} intervals: {machine_to_intervals[machine_id]}") # Optional Debug print

    # b) Precedence Constraints within each Job:
    # Ensure that tasks within the same job are executed in the specified order.
    # The start time of a task must be greater than or equal to the end time of its predecessor task in the same job.
    for job_id in all_jobs:
        # Iterate through tasks in the job, up to the second-to-last task.
        for task_index in range(len(jobs_data[job_id]) - 1):
            # Get the end variable of the current task (the predecessor).
            prev_task_end = all_tasks[(job_id, task_index)][1]
            # Get the start variable of the next task in the sequence (the successor).
            next_task_start = all_tasks[(job_id, task_index + 1)][0]
            # Add the constraint: next_task must start only after prev_task ends.
            model.Add(next_task_start >= prev_task_end)
            # print(f"Debug: Job {job_id}, Task {task_index+1} start >= Task {task_index} end") # Optional Debug print


    # --- 5. Define the Objective: Minimize Makespan ---
    # The makespan is the time when the entire schedule completes, i.e.,
    # when the last task of *any* job finishes.
    # We want to find the schedule that minimizes this completion time.

    # Create an integer variable to represent the makespan.
    makespan = model.NewIntVar(0, horizon, 'makespan')

    # Collect the end time variables of the *last* task of each job.
    last_task_end_times = []
    for job_id in all_jobs:
        # Find the index of the last task for the current job.
        last_task_index = len(jobs_data[job_id]) - 1
        # Get the end variable of this last task.
        last_task_end_times.append(all_tasks[(job_id, last_task_index)][1])

    # Add a constraint that the 'makespan' variable must be equal to the maximum
    # of the end times collected above.
    model.AddMaxEquality(makespan, last_task_end_times)

    # Set the objective of the model: find the solution that minimizes the 'makespan' variable.
    model.Minimize(makespan)

    # --- 6. Solve the Model ---
    print("Solving the model...")
    # Create a solver instance.
    solver = cp_model.CpSolver()
    # Optional: Set a time limit for the solver (e.g., 30 seconds).
    # solver.parameters.max_time_in_seconds = 30.0

    # Call the solver to find a solution.
    status = solver.Solve(model)
    print("-" * 30)

    # --- 7. Display Results ---
    # Check the status returned by the solver.
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Solution Found:')
        # Print the status (Optimal means proven best, Feasible means a valid solution found).
        print(f'  Status         : {solver.StatusName(status)}')
        # Print the minimum makespan found.
        print(f'  Optimal Makespan: {solver.ObjectiveValue()}')
        # Print the time taken by the solver.
        print(f'  Wall Time      : {solver.WallTime()} seconds')
        print('\nDetailed Schedule:')

        # Prepare a structure to display the schedule organized by machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id in all_jobs:
            for task_index, (machine_id, duration) in enumerate(jobs_data[job_id]):
                # Retrieve the solved start and end times for each task from the solver.
                start_time = solver.Value(all_tasks[(job_id, task_index)][0])
                end_time = solver.Value(all_tasks[(job_id, task_index)][1])
                # Store the task details for printing.
                assigned_jobs[machine_id].append({
                    'job': job_id,
                    'task': task_index,
                    'start': start_time,
                    'end': end_time,
                    'duration': duration
                })

        # Print the schedule, machine by machine, with tasks sorted by start time.
        output = ""
        for machine_id in all_machines:
             # Sort tasks assigned to this machine based on their start time for clarity.
            assigned_jobs[machine_id].sort(key=lambda x: x['start'])

            output += f'Machine {machine_id}:\n'
            # Print details for each task on the machine.
            for task in assigned_jobs[machine_id]:
                output += f'  Job {task["job"]} Task {task["task"]}: Start={task["start"]}, End={task["end"]}, Duration={task["duration"]}\n'
        print(output)

    elif status == cp_model.INFEASIBLE:
        # If the solver determined the problem has no possible solution under the given constraints.
        print('No solution found. The problem is infeasible.')
    else:
        # If the solver stopped for other reasons (e.g., time limit reached before finding optimal/feasible).
        print('Solver stopped before finding a solution.')
        print(f'  Status: {solver.StatusName(status)}')

# --- Run the solver ---
if __name__ == '__main__':
    solve_simple_jssp()
