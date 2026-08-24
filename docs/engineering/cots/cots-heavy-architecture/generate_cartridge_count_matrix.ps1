param(
    [string]$Directory = $PSScriptRoot
)

$baseRows = Import-Csv -LiteralPath (Join-Path $Directory 'CO2_GAS_SIZING_ANALYSIS.csv') |
    Group-Object scenario,temp_C,depth_m |
    ForEach-Object { $_.Group[0] } |
    Sort-Object @{Expression = {[array]::IndexOf(@('warm','nominal','cold'), $_.scenario)}}, @{Expression = {[double]$_.depth_m}}

$candidates = @(
    [pscustomobject]@{mpn='85202Z'; charge=33; water=45; diameter=1.000; length=5.000; mass='UNVERIFIED'; support='PUBLISHED CONFIGURATION SUPPORTED'},
    [pscustomobject]@{mpn='86202Z'; charge=38; water=50; diameter=1.180; length=4.650; mass='UNVERIFIED'; support='PUBLISHED CONFIGURATION SUPPORTED'},
    [pscustomobject]@{mpn='87202Z'; charge=45; water=60; diameter=1.180; length=5.430; mass='UNVERIFIED'; support='PUBLISHED CONFIGURATION SUPPORTED; CURRENT KIT CONFIRMATION REQUIRED'},
    [pscustomobject]@{mpn='87203Z'; charge=60; water=83; diameter=1.181; length=7.047; mass='UNVERIFIED'; support='APPLICATION APPROVAL REQUIRED'},
    [pscustomobject]@{mpn='89070'; charge=70; water=100; diameter=1.180; length=8.070; mass='UNVERIFIED'; support='APPLICATION APPROVAL REQUIRED'},
    [pscustomobject]@{mpn='89086'; charge=86; water=114; diameter=1.380; length=7.480; mass='UNVERIFIED'; support='APPLICATION APPROVAL REQUIRED; LIFECYCLE UNVERIFIED'},
    [pscustomobject]@{mpn='89092'; charge=92; water=125; diameter=1.378; length=8.465; mass='UNVERIFIED'; support='APPLICATION APPROVAL REQUIRED'},
    [pscustomobject]@{mpn='89150'; charge=150; water=203; diameter=1.969; length=6.929; mass='UNVERIFIED'; support='APPLICATION AND DIMENSIONAL APPROVAL REQUIRED'}
)

$rows = foreach ($candidate in $candidates) {
    $envelopeMl = [math]::Round([math]::PI * [math]::Pow(($candidate.diameter * 25.4) / 2, 2) * ($candidate.length * 25.4) / 1000, 1)
    foreach ($count in 1..7) {
        $inventory = $candidate.charge * $count
        foreach ($base in $baseRows) {
            $designPass = $inventory -ge [double]$base.design_required_g
            $qualificationPass = $inventory -ge [double]$base.qualification_required_g
            $scenarioRows = $baseRows | Where-Object scenario -eq $base.scenario
            $designPassing = $scenarioRows | Where-Object {$inventory -ge [double]$_.design_required_g}
            $qualificationPassing = $scenarioRows | Where-Object {$inventory -ge [double]$_.qualification_required_g}
            $maxDesign = if ($designPassing) {($designPassing | Measure-Object depth_m -Maximum).Maximum} else {'UNSUPPORTED_AT_0_M'}
            $maxQualification = if ($qualificationPassing) {($qualificationPassing | Measure-Object depth_m -Maximum).Maximum} else {'UNSUPPORTED_AT_0_M'}
            [pscustomobject]@{
                manufacturer='Leland'
                cartridge_mpn=$candidate.mpn
                compatibility=$candidate.support
                cartridge_charge_g=$candidate.charge
                cartridge_count=$count
                total_inventory_g=$inventory
                scenario=$base.scenario
                temp_C=$base.temp_C
                depth_m=$base.depth_m
                theoretical_required_g=$base.theoretical_g
                design_required_g=$base.design_required_g
                qualification_required_g=$base.qualification_required_g
                design_status=$(if ($designPass) {'PASS'} else {'FAIL'})
                qualification_status=$(if ($qualificationPass) {'PASS'} else {'FAIL'})
                max_grid_design_depth_m=$maxDesign
                max_grid_qualification_depth_m=$maxQualification
                total_water_capacity_ml=$candidate.water * $count
                estimated_outer_envelope_ml=[math]::Round($envelopeMl * $count, 1)
                estimated_cartridge_mass='UNVERIFIED; total gross mass must be quoted'
                inflator_branches=$count
                reset_burden=$(if ($count -le 3) {'LOW'} elseif ($count -le 5) {'MODERATE'} else {'HIGH'})
            }
        }
    }
}

$rows | Export-Csv -LiteralPath (Join-Path $Directory 'CARTRIDGE_COUNT_MATRIX.csv') -NoTypeInformation -Encoding utf8
